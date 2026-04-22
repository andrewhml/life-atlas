# 🔧 UGREEN NAS — Services, Versions, and Known Issues

Operational reference for the UGREEN DXP6800. Complements [`nas-structure.md`](./nas-structure.md), which covers folder layout and sync topology.

Purpose:
- Track which Docker services run on the NAS and any pinned versions
- Record known bugs we're working around, so upgrades can be revisited when upstream closes the issue
- Keep paths and ports in one place that's easy to grep

---

## 🖥️ Hardware & Identity

| Attribute | Value |
|---|---|
| Model | UGREEN DXP6800 (6-bay) |
| CPU | 12th Gen Intel Core i5-1235U (Alder Lake, 2P + 8E cores, 12 threads) |
| iGPU | Intel UHD Graphics (Alder Lake-UP3 GT2) — `/dev/dri/card0`, `/dev/dri/renderD128` |
| RAM | 8 GB (7.5 GiB usable) — **tight under load** (see Capabilities below) |
| Swap | 6 GB (~3.2 GB in use during normal operation — indicates RAM pressure) |
| OS | Debian 12 (bookworm), kernel 6.12.30+ |
| Physical NICs | 2× `eth0`/`eth1`, both negotiating at 1 GbE today — confirm whether a 2.5/10 GbE variant is being capped by switch |
| UPS | **CyberPower PR1500LCDRT2U**, USB-connected. NUT daemons (`upsd`, `usbhid-ups -a ups0`, `upsmon`) running with config in `/etc/nut/`. Auto-shutdown on battery-low is configured. Verify with `upsc ups0` for live status. |
| OS hostname | `DXP6800` / prompt shows `Peddocks2` |
| Tailscale machine name | `dxp6800` |
| Tailscale full domain | `dxp6800.boston-marlin.ts.net` |
| Tailscale IPv4 | `100.120.233.118` |
| DDNS base domain | `peddocks.ddns.net` |
| Tailscale role | Exit node |

Open question: naming — `CLAUDE.md` says "Peddocks2", DDNS uses `peddocks`, Tailscale uses `dxp6800`. Shell prompt shows `Peddocks2`. Reconcile in a followup.

---

## 🗄️ Storage Architecture

### Pools

| Pool | Backing | Filesystem | Capacity | Used | Role |
|---|---|---|---|---|---|
| `/volume1` | 4× 10.9 TB HDD in MD RAID 5 + LVM (cached) | **Btrfs** | 21.8 TB | 11 TB (48%) | Main pool — Plex, Immich, `/volume1/docker/`, Media, Atlas mirror |
| `/volume2` | 1× 931 GB NVMe (`nvme1n1`), MD "RAID 1" single-member + LVM | ext4 | 901 GB | 1.6 GB (1%) | **Idle** — intended as fast app pool |
| `/mnt/@usb/sdc2` | External USB 3.6 TB | exfat | 3.6 TB | 2.3 TB (61%) | Legacy Plex content drive (`Plex Media/`). Has Synology (`@eaDir`) and Mac (`.Spotlight-V100`) metadata — lived on other systems before UGREEN. Candidate for rotating-offsite *after* contents migrated into `/volume1` and drive reformatted. |

### LVM cache (HDD acceleration)

`nvme0n1` (931 GB NVMe) is configured as an **LVM write-back cache** for `/volume1`. Hot reads and writes hit NVMe first, get destaged to HDD async. This is a big perf boost for Immich Postgres, NPM SQLite, Plex metadata, and any DB-heavy service.

- `nvme0n1p2` (916 GB) → `md2` RAID 1 (single-member) → LVM `lvmcache_cvol` → cached onto `/volume1` btrfs
- Config was pre-set by UGREEN OS; no action needed, just know it's there

### HDDs

4× **Seagate IronWolf ST12000VN0008** (12 TB nominal / 10.9 TiB formatted per drive, 7200 RPM CMR, purpose-built NAS class). Each drive has a 15.3 GB system partition + 10.9 TiB data partition. All 4 × data partitions form `md1` RAID 5 (32.7 TiB raw → 21.8 TB usable after LVM overhead). **1-drive fault tolerance only.**

Drive identities and SMART baseline (2026-04-22):

| Drive | Serial | Health | Realloc | Pending | PowerOnHrs | Temp |
|---|---|---|---|---|---|---|
| `/dev/sda` | ZRT2D8EX | PASSED | 0 | 0 | 8,900 | 38°C |
| `/dev/sdb` | ZRT2C61N | PASSED | 0 | 0 | 8,900 | 39°C |
| `/dev/sdd` | ZRT2DKE3 | PASSED | 0 | 0 | 8,900 | 36°C |
| `/dev/sde` | ZRT2DFLX | PASSED | 0 | 0 | 8,901 | 35°C |

All 4 drives: zero reallocated/pending/uncorrectable sectors, zero UDMA CRC errors. ~1 year of continuous operation. Temperatures healthy (IronWolf max 60°C). Phase 4 replication source is safe.

Minor observation: `sde` has ~18% higher write count than siblings — normal in RAID 5 + LVM cache destaging patterns. Noted, not actionable.

Synology drives (5× 7.3 TB in SHR-2): SMART baseline TBD via Synology DSM UI or SSH. **Required before Phase 4 wipe-and-repurpose decision** — the drives are ~7 years old and that history is unknown.

### Bay usage

- 4 of 6 HDD bays populated (2 empty — expansion headroom)
- 2 NVMe slots populated (`nvme0n1` cache, `nvme1n1` volume2); verify whether additional M.2 slots exist for future expansion
- 1 external USB drive (`sdc`) — contents unknown

### Installed CLI tooling

Present: `btrfs`, `rsync`, `sqlite3`, `systemctl`, `lspci`, `lsblk`, `upsc`, `tailscale`, `docker`.

Present but not in non-root `PATH` (use full path or `sudo`):
- **`smartctl`** — installed (smartmontools 7.3-1+b1); lives at `/usr/sbin/smartctl`. `/usr/sbin` isn't in `andrewhml`'s PATH by default.
- **`ethtool`** — same story, in `/usr/sbin/ethtool`. Confirmed working via sudo earlier.

Missing / notes:
- **`cron`** binary — scheduled tasks use systemd timers; `/etc/cron.d/` only has Debian defaults (`e2scrub_all`, `sysstat`). If adding new scheduled rsync/backup jobs, prefer systemd timers for consistency.

### Known-state caveat — unmet package deps

`apt install` on this host reports pre-existing unmet deps (e.g., `exiv2: libexiv2-27 (= 0.27.6-1)`, `libopengl0: libglvnd0 (= 1.7.0-2101~22.04)`). These are UGREEN-OS customizations — UGOS ships a modified Debian with pinned package versions that don't always match upstream. **Do NOT run `apt --fix-broken install`** — it could downgrade or remove packages UGREEN depends on for admin UI, Docker management, or hardware integration. Leave alone until something actively breaks.

---

## 🌐 Network

### Physical

- 2× physical NICs (`eth0`, `eth1`) both negotiating **1 GbE** — NICs likely support higher, but the rest of the chain doesn't.
- **Switch is 15–20 years old, gigabit-era.** Confirms at least 1 GbE negotiation, but age-related reliability concerns (buffers, capacitors, fan wear) likely cap real sustained throughput well below the line rate.
- **In-wall cabling is Cat 5** (from early 2000s, not Cat 5e). Cat 5 is officially rated for 100 Mbps; gigabit often works on short runs but degrades with length, quality, interference.
- Realistic sustained throughput: likely 250–500 Mbps, not 1 Gbps. A 10 TB replication pass over this fabric = many hours to a full day.
- Both UGREEN and Synology plug into the same old switch. Mesh router upstream is TP-Link Deco X55 Pro (2.5 GbE capable).
- Docker bridge networks (`br-*`, `veth*`) are virtual; their 10 Gbps readings are cosmetic.

### Internet

- ISP: Xfinity. Down ~755 Mbps / Up ~72 Mbps (speedtest).
- Public IP: **likely dynamic** (Xfinity residential default). Confirm if paying for a static.
- DDNS hostname: `peddocks.ddns.net` (handles IP rotation for inbound service access).

### Implications

- **Offsite via cloud backup** is viable for a critical tier (~1 TB: Atlas docs + Obsidian + photos) — ~25 hours initial upload at 72 Mbps; ongoing deltas tractable. Not this phase, but when ready, ~$5–10/month Backblaze B2 tier makes sense.
- **Switch upgrade** is the single highest-leverage cheap hardware move. Modern 5-port 2.5 GbE switch ($40–80) would likely 2–3× real throughput. Parked as a recommended future buy.
- **Dynamic IP + Access List** — the Access List uses the current home IP directly. If Xfinity rotates, Immich's public URL will 403 from home until the Access List is updated. See Known Issues for the "IP rotated" recipe.

---

## 💡 Capabilities & Constraints

### Opportunities unlocked by hardware

- **iGPU — Plex ✓, Immich ✗.** PlexHW has `/dev/dri/renderD128` and `/dev/dri/card0` mapped (transcoding accelerated). Immich-SERVER does NOT — all ML (face detection, CLIP search, thumbnail gen) runs on CPU. **Easy win to enable:** map `/dev/dri` into Immich compose, add relevant group_add entries, set Immich ML hardware-accel env vars, redeploy. Expect significantly faster thumbnail pass and ML indexing, lower CPU load.
- **Btrfs on volume1** → free point-in-time snapshots (`btrfs subvolume snapshot`) before container upgrades, reflinks for cheap copy-on-write, `btrfs send/receive` for delta-efficient replication to another Btrfs target.
- **UPS with USB feedback** → clean shutdown on power loss protects SQLite/Postgres/Btrfs consistency. Verify NUT or apcupsd is actually running and configured.
- **Volume2 (901 GB NVMe, empty)** → ideal location for Docker service DB paths (Immich Postgres, NPM SQLite) for lower latency than going through HDD pool + LVM cache. Caveat: no redundancy, so anything on volume2 needs replication to volume1 or Synology.
- **External 3.6 TB USB drive (`sdc`)** → candidate for rotating-offsite if contents can be moved/cleared. Physical portability solves the offsite gap for the critical data tier (photos + vault + docs).

### Constraints

- **RAM: 8 GB total.** Active Docker RAM ~2.1 GB (Immich ~900 MB, Immich-LEARNING ~250 MB, Plex ~120 MB, Tailscale ~112 MB, rest ~100 MB or less). Swap shows 3.2 GB used but most is inactive paged-out memory; 2.4 GiB still "available." Tight but workable. Adding a light container (CouchDB, Authelia) should fit. A 16 GB or 32 GB SO-DIMM upgrade still worth considering for headroom once future phases land.
- **RAID 5 = 1-drive fault tolerance.** One drive failure during rebuild exposes full pool loss. Worth a conversion to RAID 6 (parity doubled) if bays permit, but requires downtime and spare drives. Not urgent; document as accepted risk.
- **Volume2 has no redundancy** (MD RAID 1 with a single member). Anything placed there must be replicated elsewhere.
- **Network at 1 GbE** caps backup throughput; ~24 hrs for a full 10 TB replication pass.

---

## 🐳 Docker Services

All containers live under `/volume1/docker/<service>/`. Stack definitions live in Portainer.

| Service | Purpose | Public URL (via NPM) | Internal port |
|---|---|---|---|
| Nginx Proxy Manager | Reverse proxy / TLS / access control | admin UI on `:81` | 80 / 81 / 443 |
| Portainer | Container management | `portainer.peddocks.ddns.net` | — |
| Immich | Self-hosted photos | `immich.peddocks.ddns.net` | **8212** (non-default) |
| Plex | Media server | `plex.peddocks.ddns.net` | 32400 |
| Overseerr | Plex request manager | `overseerr.peddocks.ddns.net` | 5055 |
| Sonarr | TV indexer / downloader | `sonarr.peddocks.ddns.net` | 8989 |
| Radarr | Movie indexer / downloader | `radarr.peddocks.ddns.net` | 7878 |
| Lidarr | Music indexer / downloader | — | 8686 |
| qBittorrent | Torrent client | `qbittorrent.peddocks.ddns.net` | 8080 |
| Gluetun | VPN gateway (wraps qBittorrent) | — | — |
| Calibre | eBook server | `calibre.peddocks.ddns.net` | 8083 |
| Tailscale | Tailnet exit node | — | — |

---

## 📌 Pinned Versions

When a `docker-compose.yml` has an image tag other than `latest`, record *why* here so future upgrades have a rationale.

| Service | Pinned to | Reason | When to unpin |
|---|---|---|---|
| Nginx Proxy Manager | `jc21/nginx-proxy-manager:latest` (likely 2.14.0) | Pin image tag explicitly once version confirmed from UI. Attempted downgrade to 2.13.6 failed (migration mismatch — 2.14.0's `trust_forwarded_proto` migration isn't in 2.13.6). NOW() bug persists in both 2.13.7 and 2.14.0. See Known Issues. | When a new release ships with the NOW() fix — verify with a test Access List save before unpinning. |

---

## 🐛 Known Issues

Active workarounds for upstream bugs. Each should have an upstream tracker and a clear "resolved when" condition.

### NPM SQLite `NOW()` error (🔴 active)

- **Summary:** NPM emits MySQL `NOW()` in SQLite UPDATE queries against the `modified_on` column. Any UI edit to a record (Access List, proxy host) silently fails. Other functionality (new hosts, SSL issuance, redirects) works.
- **Affected versions:** v2.13.7 and v2.14.0. The `sqlite3 → better-sqlite3` swap in 2.13.7 likely introduced it; 2.14.0 did not fix it. No v2.14.1+ exists yet.
- **Upstream:** [NginxProxyManager/nginx-proxy-manager#5284](https://github.com/NginxProxyManager/nginx-proxy-manager/issues/5284) — marked closed but bug persists, so likely closed as duplicate/won't-fix; real resolution TBD.
- **Downgrade path is blocked:** 2.14.0 introduced the `20260131163528_trust_forwarded_proto.js` migration. Downgrading to 2.13.6 triggers `migration directory is corrupt` because Knex sees a migration record for a file it can't find.
- **Workaround in use — direct DB UPDATE to `advanced_config`:** Bypass the broken UPDATE code path by writing raw nginx `allow`/`deny` directives straight to the SQLite `proxy_host.advanced_config` column. Restart the NPM container to regenerate nginx configs from DB. Per-host, surgical, reversible. Community-validated pattern (via GitHub issues #1105, #4441 and NPM docs on Advanced config).
  - Example:
    ```bash
    sqlite3 /volume1/docker/npm/data/database.sqlite \
      "UPDATE proxy_host SET advanced_config = 'allow <IP>; deny all;' WHERE domain_names LIKE '%immich%';"
    # Then restart NPM container to apply
    ```
  - Caveat: a future UI edit to the same host will wipe this (save will fail due to NOW() bug, and even if it succeeded, would overwrite advanced_config unless re-entered)
- **Harder workaround — migration record surgery + downgrade:** `DELETE FROM knex_migrations WHERE name = '20260131163528_trust_forwarded_proto.js';` then image swap to 2.13.6. Leaves orphan column in `proxy_host`; 2.13.6 tolerates it. Riskier; only do if DB-UPDATE path isn't enough.
- **Resolved when:** Issue #5284 (or successor) fixed + new release ships — verify with a test Access List save before unpinning.
- **First seen:** 2026-04-22

### Home IP rotation breaks Access List (🟡 operational risk)

- **Summary:** Xfinity residential IP is dynamic. The "Admin Utilities" Access List has the current home IP hardcoded (`73.100.35.222` as of 2026-04-22). If Xfinity rotates, `immich.peddocks.ddns.net` and `portainer.peddocks.ddns.net` return 403 from home until updated.
- **Detection:** try `https://immich.peddocks.ddns.net` from home Wi-Fi. 403 = IP rotated.
- **Recipe to update:** Find new IP (`curl -s ifconfig.me` from home Mac), then over SSH to NAS (while NPM `NOW()` bug persists):
  ```bash
  # Find the client row in access_list_client for the old IP
  sudo sqlite3 /volume1/docker/npm/data/database.sqlite \
    "SELECT id, address FROM access_list_client WHERE address LIKE '73.100%';"
  # Update the address to the new IP (substitute <id> and <new-ip>)
  sudo sqlite3 /volume1/docker/npm/data/database.sqlite \
    "UPDATE access_list_client SET address = '<new-ip>' WHERE id = <id>;"
  # Restart NPM to regenerate nginx config
  ```
  (Schema note: confirm `access_list_client` table name on first run — NPM may use a slightly different name. `.schema` inside sqlite3 will show all tables.)
- **Long-term fix:** Either pay Xfinity for static IP, or shift hardening to DuckDNS/Cloudflare Tunnel with Zero Trust Access (closes the dynamic-IP brittleness).

### Let's Encrypt force-renewal loop → rate limit cycle (🟡 understood + accepted)

- **Summary (diagnosed 2026-04-22):** NPM's internal Node.js scheduler fires hourly by design and applies `--force-renewal` **unconditionally** to any cert within 30 days of expiry — see [DeepWiki reference](https://deepwiki.com/NginxProxyManager/nginx-proxy-manager/3.5-certificate-renewal-system). With 9 certs issued at the same time, they all enter the 30-day window together, all get force-renewed every hour, and LE's "5 issuances per 168h per identifier" rate limit gets burned through within 5 hours. Remaining attempts hit HTTP 429 for ~1 week until the rate window clears. This is NOT an NPM bug — it's documented behavior. Each successful force-renewal resets the cert's 90-day lifetime, causing them all to re-align and creating the cycle.
- **Current state (verified 2026-04-22):** All 9 certs renewed successfully, expire 2026-07-20/21 (~89 days remaining). Services healthy. Rate limit clears ~2026-04-29.
- **Recurrence cycle:** Next trigger ~2026-06-20 when certs cross into the 30-day renewal window. Expect a week of rate-limit noise, then quiet again. Cycle repeats every ~60 days indefinitely unless resolved structurally.
- **Workaround — accepted (option B):** Do nothing. Certs stay valid. Only impact is noisy logs for ~1 week every 2 months.
- **Structural fix (option A, deferred):** Register a proper domain (candidate: **`peddocks.io`** to continue existing naming) + move DNS to Cloudflare (free tier) + reissue as a single wildcard `*.peddocks.io` via DNS-01 challenge. Cost: `.io` TLD is ~$30-50/yr (premium TLD — `.com` would be ~$10/yr if user preferred that). Reduces 9 certs → 1, eliminating rate-limit risk entirely. Bonus benefits: enables Cloudflare Tunnel + Zero Trust Access for Immich hardening (replaces current IP-allowlist brittleness), removes dynamic-IP rotation problem, cleaner DDNS via Cloudflare API. Queue alongside the Phase 4 hardware purchases.
- **First diagnosed:** 2026-04-22

---

## 📁 Key Paths

| Path | Contents |
|---|---|
| `/volume1/docker/` | All Docker service data roots (backup target) |
| `/volume1/docker/npm/data/` | NPM SQLite DB + config |
| `/volume1/docker/npm/letsencrypt/` | Let's Encrypt certs |
| `/volume1/docker/immich/` | Immich library, config, Postgres data |
| Media shares (Plex content) | See `nas-structure.md` |

---

## 🔭 Watch List

Upstream threads worth checking before major upgrades or when planning related work:

- [NPM #5284 — SQLite NOW() bug](https://github.com/NginxProxyManager/nginx-proxy-manager/issues/5284) — unpin NPM when resolved
- [Immich 2FA / TOTP feature discussions](https://github.com/immich-app/immich/discussions/23339) — rethink auth layer if native 2FA ships

---

## 🪜 Future config improvements (no new hardware needed)

Actionable config/migration work to improve performance and backup posture. Sequence matters — do higher items before lower ones.

### Leverage idle `/volume2` NVMe (901 GB) for performance

Context: `/volume1` is already LVM-cache-accelerated by `nvme0n1` (916 GB), so moving to `/volume2` (`nvme1n1`) only pays off for workloads that exceed the cache working set or need guaranteed SSD latency. `/volume2` has **no redundancy** (single drive, Basic LVM) — anything persistent there needs replication to `/volume1`.

Targets in recommended order:

1. **Immich ML cache** (`/volume1/docker/immich/cache` → `/volume2/immich/cache`) — ephemeral, safe on non-redundant storage. Biggest win for Phase 2 dedup + ML indexing speed post-iGPU enablement.
2. **Plex transcoding scratch** — configure via Plex UI (Settings → Transcoder → Transcoder temporary directory → `/volume2/plex-transcode/`). Ephemeral, no replication needed.
3. **Immich Postgres DB** (`/volume1/docker/immich/db` → `/volume2/immich/db`) — biggest perf gain, but requires nightly `pg_dump` + rsync to `/volume1/docker-bak/` or similar. Don't do this step without the replication job set up first.
4. **Future: LiveSync CouchDB (Phase 5)** — start new data directly on `/volume2` with the same replication pattern.

**Explicitly skip:** NPM SQLite, Portainer config, Sonarr/Radarr DBs — small working sets already fit in LVM cache, no meaningful benefit. Media libraries (Plex content, Immich originals) — too large for `/volume2`.

### Enable Immich iGPU acceleration

See task #11. Plex has `/dev/dri` mapped; Immich-SERVER and Immich-LEARNING don't. Adding it uses the Intel UHD iGPU for ML (OpenVINO) and video transcoding (Quick Sync). Meaningfully faster thumbnail/face/CLIP pass; lower CPU and swap pressure.

### Migrate USB drive contents into `/volume1`

`/mnt/@usb/sdc2/Plex Media/` contains ~2.3 TB of legacy Plex content with Synology/Mac metadata artifacts. Plan:
1. Verify content isn't duplicated in `/volume1` (dedup by file path or hash sample)
2. rsync to `/volume1/Media/...` appropriate subfolder
3. Verify Plex can still see it after symlink/path update
4. Reformat `sdc` to a native filesystem (ext4 or btrfs; drop exfat)
5. Drive becomes available as rotating-offsite target for the critical data tier

### Install `smartmontools`

See task #12. Unblocks Phase 4 drive health baselining. `sudo apt install smartmontools`.

### Audit / replace unused-but-still-configured services

E.g., `73.143.122.9` in the "Admin Utilities" Access List — unknown origin. When the NPM NOW() bug is fixed upstream and Access List editing works again, review and prune.

---

## 🛒 Hardware commitments + future buys

### Committed (2026-04-22) — part of Phase 4 execution

| Item | Rationale | Ballpark |
|---|---|---|
| 2× Seagate IronWolf 12 TB | Match existing 4 drives; populate empty UGREEN bays; enables RAID 6 migration for 2-drive fault tolerance, ~44 TB usable (up from 22 TB RAID 5) | ~$250 each × 2 = $500 |
| 5-port 2.5 GbE unmanaged switch (e.g., TP-Link TL-SG105-M2, QNAP QSW-1105-5T) | Replaces 15–20 year old gigabit switch; unlocks UGREEN's native 2.5 GbE NIC capability | $40–60 |
| Cat 5e/6 patch cables for NAS-to-switch runs | Local patches to ensure 2.5 GbE negotiation | ~$15 |

### Future (not committed, noted for eventual consideration)

| Item | Rationale | Ballpark |
|---|---|---|
| SO-DIMM RAM upgrade to 16 GB or 32 GB | Headroom for LiveSync CouchDB, Authelia, future service additions | $30–80 |
| Cat 6 in-wall re-runs between NAS and other rooms | If long in-wall Cat 5 runs cap below 2.5 GbE after switch upgrade | $100–300 depending on run complexity |
| Backblaze B2 subscription (or equivalent) for critical-tier cloud offsite | ~$5–10/month for ~1 TB; closes offsite gap for photos + vault + docs | $5–10/mo |
| Register `peddocks.io` + migrate to Cloudflare | Solves LE rate-limit cycle (wildcard cert), removes dynamic-IP Access List brittleness, unlocks Cloudflare Tunnel for better Immich hardening. User preference for `.io` domain, matches existing `peddocks.ddns.net` naming. See task #13 + Known Issues. | `.io` ~$30-50/yr; Cloudflare free |
| 10 GbE NIC + switch upgrade for UGREEN↔Mac path | Only worth it if Mac gets 10 GbE too; diminishing returns below that | $150–400 |

---

## 🔄 Review Cadence

Review this file:
- Before any major NAS maintenance window
- When `/audit` surfaces drift in this area
- Quarterly at minimum — outdated pins are nearly as bad as no pins
