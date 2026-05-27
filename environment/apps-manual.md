# Native app inventory (non-brew)

Apps and parity-required items on AM2 that the Brewfile does NOT install. Walk this top-to-bottom during AM5 onboarding (plan 0007 Phase 5f).

**Inventory captured 2026-05-25 (host=AM2, M2 Pro) during plan 0007 Phase 4** from 8 enumeration surfaces: `/Applications`, `mas list` (already in Brewfile), Login Items, LaunchAgents, fonts, browser extensions, preference panes / system extensions, CLI tools outside brew.

Anything in [`environment/Brewfile`](Brewfile) is **not** repeated here. That includes: `font-meslo-lg-nerd-font`, `ghostty`, `display_switch` + `m1ddc`, all CLI formulas, and the 4 npm globals (`@google/gemini-cli`, `@openai/codex`, `planpong`, `vercel`).

Mac App Store apps live in the "Mac App Store apps" section below — they used to live in the Brewfile under `mas`, but `mas install` is broken on macOS 26.5 (requires sudo + several ADAM IDs return "No apps found"). Install MAS apps via the App Store GUI.

---

## AI clients (native installers)

### Claude.app
- **Install:** https://claude.ai/download (macOS)
- **Purpose:** Anthropic Claude desktop client
- **Setup notes:** Sign in. (The Claude **Code** CLI is part of the harness clone, not this app.)

### Codex.app
- **Install:** https://chat.openai.com/codex (OpenAI installer)
- **Purpose:** OpenAI Codex desktop client
- **Setup notes:** Sign in via OpenAI account.

### ChatGPT.app
- **Install:** https://openai.com/chatgpt/download
- **Purpose:** OpenAI ChatGPT desktop client
- **Setup notes:** Sign in.

---

## Browsers

### Brave Browser
- **Install:** https://brave.com/download/ — `.dmg`, drag to Applications
- **Purpose:** Primary browser
- **Setup notes:** Sign in to Brave Sync to recover bookmarks, settings, and extensions (10 extensions on AM2; sync handles them automatically).

### Firefox
- **Install:** https://www.mozilla.org/firefox/new/
- **Purpose:** Secondary browser
- **Setup notes:** Sign in to Firefox account for bookmark/setting sync.

### Google Chrome
- **Install:** https://www.google.com/chrome/
- **Purpose:** Compatibility / Google Workspace
- **Setup notes:** Sign in to Google account. 12 extensions on AM2; sync via Chrome account.

---

## Adobe Creative Cloud (one installer, many sub-apps)

### Adobe Creative Cloud (the installer/launcher)
- **Install:** https://creativecloud.adobe.com/apps/download/creative-cloud
- **Purpose:** Manages all Adobe app installs and licensing
- **Setup notes:** Sign in with Adobe ID + verify subscription. Then install each sub-app via the CC app:

| Sub-app | Notes |
|---|---|
| Acrobat DC | PDF |
| Illustrator 2026 | Vector |
| Lightroom CC | Photo (NOT Lightroom Classic — see plan 0005 for the photo workflow) |
| Media Encoder 2026 | Required by Premiere export |
| Photoshop 2026 | Raster |
| Premiere Pro 2026 | Video |

LaunchAgents auto-installed by CC: `com.adobe.AdobeCreativeCloud`, `com.adobe.AdobeDesktopService`, `com.adobe.ARMDCHelper.*`, `com.adobe.ccxprocess`, `com.adobe.GC.Invoker-1.0` (both user + system). No manual action needed for these.

---

## Communication

### Discord
- **Install:** https://discord.com/download
- **Setup notes:** Sign in.

### WhatsApp (desktop)
- **Install:** https://www.whatsapp.com/download or via Mac App Store
- **Setup notes:** Pair via QR code from phone.

### Spark Desktop (Spark mail)
- **Install:** https://sparkmailapp.com/
- **Setup notes:** Sign in to recover account list.

### Notion
- **Install:** https://www.notion.so/desktop
- **Setup notes:** Sign in.

### Zoom
- **Install:** https://zoom.us/download
- **Setup notes:** Sign in. (`us.zoom.updater.gui.501.*` LaunchAgents come with the app.)

---

## Productivity

### Raycast
- **Install:** https://www.raycast.com/
- **Setup notes:** Sign in for cloud sync of snippets, scripts, extensions. (Login Item.)

### Figma
- **Install:** https://www.figma.com/downloads/
- **Setup notes:** Sign in. (`FigmaAgent` Login Item handles updates.)

### Obsidian
- **Install:** https://obsidian.md
- **Setup notes:** Vault location decision is out of scope (see existing life-atlas issue tracking the vault strategy).

### OmmWriter
- **Install:** App Store or https://ommwriter.com
- **Setup notes:** Distraction-free writing.

### Screen Studio
- **Install:** https://screen.studio/
- **Setup notes:** Sign in / license key. Screen recording for tutorials.

---

## Media / photo / video

### Spotify
- **Install:** https://www.spotify.com/download
- **Setup notes:** Sign in. macOS Spotify app (not the web player).

### Plex / Plexamp
- **Install:** https://www.plex.tv/media-server-downloads/ + https://www.plex.tv/plexamp
- **Setup notes:** Sign in to plex.tv account. NAS Plex server lives at `plex.peddocks.ddns.net` (see device-schemas/nas-services.md).

### CapCut
- **Install:** https://www.capcut.com/ or Mac App Store
- **Setup notes:** Sign in.

### HandBrake
- **Install:** https://handbrake.fr/downloads.php
- **Setup notes:** Standalone video transcoder. Pairs with `brew install ffmpeg` for the CLI.

### OBS Studio
- **Install:** https://obsproject.com/download
- **Setup notes:** Installs the OBS Virtual Camera system extension (`com.obsproject.obs-studio.mac-camera-extension`). Approve in System Settings > Privacy & Security after install.

### VLC
- **Install:** https://www.videolan.org/vlc/
- **Setup notes:** Standalone media player; covers what QuickTime can't.

---

## Backup / sync / network

### Carbon Copy Cloner
- **Install:** https://bombich.com/download (or App Store) + paid license
- **Purpose:** Disk cloning (powers external SSD backups per plan 0005)
- **Setup notes:** Sign in / enter license. Recreate the existing backup tasks: Carbonizer → Carbonizer_BU on NAS, Carbonizer → Noisy Cricket clone. (Task definitions are not portable between Macs out-of-the-box; recreate via the UI.)

### DaisyDisk
- **Install:** https://daisydiskapp.com/ (or App Store) + license
- **Purpose:** Disk usage visualizer
- **Setup notes:** License key.

### Tailscale
- **Install:** https://tailscale.com/download/macos
- **Purpose:** Mesh VPN; provides access to NAS / brother's UGREEN / etc.
- **Setup notes:** Sign in. Installs the **Tailscale Network Extension** system extension (`io.tailscale.ipn.macsys.network-extension`) — approve in System Settings > Privacy & Security after install.

### UGREEN NAS app
- **Install:** From UGREEN: https://nas.ugreen.com/pages/download (or via the NAS web UI download link)
- **Purpose:** Native client for the UGREEN DXP6800 (Peddocks2)
- **Setup notes:** Sign in to UGREEN account; pair with NAS over LAN.

### Google Drive (Desktop)
- **Install:** https://www.google.com/drive/download/
- **Purpose:** Mounts `~/Atlas/` on each Mac. Required for life-atlas to work.
- **Setup notes:** Sign in with Google account. Enable streaming/mirroring per preference. (Login Item.)

---

## System / hardware

### BetterDisplay
- **Install:** https://github.com/waydabber/BetterDisplay (also a cask: `waydabber/betterdisplay/betterdisplay`). The `waydabber/betterdisplay` tap is in the Brewfile but the cask isn't declared because the **app itself** is installed natively on both machines; the tap is there for the separate `betterdisplaycli` formula (see below).
- **Purpose:** Display management for external monitors (especially the DDC/CI control loop with `display_switch`)
- **Setup notes:**
  - Login Item.
  - License if you bought one.
  - **The `betterdisplaycli` companion is required if `display_switch` is in use** — it's installed via the Homebrew formula (declared in `environment/Brewfile`), not the GUI. See the `betterdisplaycli` entry below for the Xcode prereq and the cask-shim trap to avoid.

### Mos (smooth scrolling for non-Apple mice)
- **Install:** https://mos.caldis.me/ (download .dmg)
- **Purpose:** Smooth scrolling normalization
- **Setup notes:** Login Item. Allow Accessibility permission.

### Logi Options+
- **Install:** https://www.logitech.com/en-us/software/logi-options-plus.html
- **Purpose:** Logitech device configuration (mouse, keyboard, etc.)
- **Setup notes:** Installs `com.logi.optionsplus.plist` + `com.logitech.LogiRightSight.Agent.plist` LaunchAgents.

### VIA (mechanical keyboard programmer)
- **Use:** https://usevia.app/ — web app, no install. Re-flashes keymap layers on QMK/VIA-compatible keyboards directly in the browser via WebHID.

---

## Editors / terminals

### Visual Studio Code
- **Install:** https://code.visualstudio.com/ (or `brew install --cask visual-studio-code` if you want to bring it into brew management)
- **Setup notes:** Sign in to Settings Sync (Microsoft account) for extensions + settings. Issue #48 in life-atlas tracks the long-term VS Code sync strategy.

---

## Fonts (user-installed, beyond brew casks)

`~/Library/Fonts/` on AM2 contains licensed font families:

- **Butler** family (14 weights including stencil variants)
- **Code Pro** family (Black, Bold, Demo, Light variants)

If you have the original purchase / download archive, drag the `.otf` files into `~/Library/Fonts/` on AM5 (or use Font Book's "Install Font" action). If not, re-purchase from the original source (Butler is by Fabian De Smet on Behance; Code Pro is by Fontfabric).

Recommendation: zip `~/Library/Fonts/*.otf` on AM2 and stash a copy in Atlas (`~/Atlas/config/fonts/` if you want to formalize a fonts subfolder, or as a one-off backup) to avoid the re-purchase question.

---

## Browser extensions (manual review / sync)

| Browser | Extension count on AM2 | Recovery approach |
|---|---|---|
| Brave Browser | 10 extensions | Sign in to **Brave Sync** on AM5 — sync chain handles it. Confirm in chrome://extensions after sign-in. |
| Google Chrome | 12 extensions | Sign in to Chrome account on AM5; extensions auto-install from your account profile. |
| Firefox | (not enumerated) | Sign in to Firefox account; extensions sync automatically. |

If you want a hand-curated list of extensions per browser (rather than relying on sync), open chrome://extensions on AM2 and screenshot/export the IDs; add a sub-bullet here. Not done in the initial inventory because browser-sync is reliable for personal use.

---

## CLI tools outside brew

### Python user packages (via `pip3 install --user`)

`pip list --user` on AM2 shows: `brotli`, `cffi`, `charset-normalizer`, `cssselect2`, `et_xmlfile`, `fonttools`, `greenlet`, `lxml`, and more. These are mostly transitive dependencies of other tools (e.g., `fonttools` for font processing, `lxml` for various XML/HTML tasks). On AM5 they'll be installed on-demand the first time a tool needs them; no proactive action required.

### Brewfile callouts (entries with non-obvious requirements)

- **`betterdisplaycli`** — formula `waydabber/betterdisplay/betterdisplaycli`. Installs the real BetterDisplay CLI binary to `/opt/homebrew/bin/betterdisplaycli`. Three gotchas worth knowing:
  - **No bottle published** — `brew bundle` will compile from source via Swift. This requires **full Xcode ≥14** (`/Applications/Xcode.app`), not just Command Line Tools. If `brew install` errors with a missing Swift toolchain, install Xcode from the App Store first.
  - **Do not confuse with the cask shim.** The BetterDisplay app cask (`waydabber/betterdisplay/betterdisplay`) installs a wrapper at the same path `/opt/homebrew/bin/betterdisplaycli` whose entire content is `exec '/Applications/BetterDisplay.app/Contents/MacOS/BetterDisplay' "$@"`. Calling it spawns extra GUI instances instead of acting as a CLI — unsuitable for `display_switch`'s LaunchAgent. If `brew bundle install` fails on the linking step because the cask shim is already at that path, run **`brew link --overwrite betterdisplaycli`** — that makes the formula's real binary win at `/opt/homebrew/bin/betterdisplaycli` without removing the cask (do **not** `brew uninstall --cask betterdisplay`; that removes the BetterDisplay GUI app entirely). Observed in practice: AM5's `brew bundle install` needed the `--overwrite` step; AM2's did not (the formula install overwrote the shim cleanly without intervention — reason unclear, mention it if you need to debug on a third machine). The empirical proof and the plan around this live in `docs/plans/0008-display-config-sync.md`.
  - **Alternative: GUI "Install CLI tool" menu action** in BetterDisplay → Settings drops a different ~218 KB launcher at `/usr/local/bin/betterdisplaycli` (`root:wheel`). Works correctly but isn't Brewfile-managed; documented here for historical context — AM2 originally used this path before the 2026-05-26 pivot to the formula.

---

## Login Items (set up after each app installs)

These auto-launch at login on AM2. Most are set up automatically by their parent app's install. The ones to verify manually after AM5 onboarding:

- BetterDisplay → enable in BetterDisplay > Settings > Launch at Login
- Google Drive → Drive sets it during setup
- Meeter → enable in Meeter preferences
- Mos → enable in Mos preferences
- NordVPN → enable in NordVPN preferences
- Raycast → enable in Raycast > Settings > General > Launch at Login
- (FigmaAgent and Adobe updaters install themselves)

---

## LaunchAgents to be aware of (informational; mostly auto-installed)

| Path | Source | Action on AM5 |
|---|---|---|
| `~/Library/LaunchAgents/ai.hermes.gateway.plist` | Hermes (unknown app — investigate or skip) | Likely AM2-specific; skip unless you remember the app |
| `~/Library/LaunchAgents/com.adobe.GC.Invoker-1.0.plist` | Adobe Creative Cloud | Auto |
| `~/Library/LaunchAgents/com.dreamhome.sweepstakes.plist` | Unknown — likely cruft | Skip; investigate on AM2 if you care |
| `~/Library/LaunchAgents/com.google.GoogleUpdater.wake.plist` | Google updater | Installed with any Google app |
| `~/Library/LaunchAgents/com.google.keystone.agent.plist` | Google keystone | Auto with Google products |
| `~/Library/LaunchAgents/homebrew.mxcl.display_switch.plist` | brew tap `haimgel/tools` | Installed by `brew bundle` (in Brewfile) |
| `~/Library/LaunchAgents/us.zoom.updater.gui.501.*.plist` | Zoom updater | Installed with Zoom |

---

## System extensions (need approval in System Settings after install)

Approval prompt appears the first time the parent app launches; usually a one-time gate.

| Extension | Parent app | State on AM2 |
|---|---|---|
| Tailscale Network Extension | Tailscale.app | activated enabled |
| OBS Virtual Camera | OBS Studio | activated enabled |

---

## Mac App Store apps

These used to be `mas` entries in the Brewfile. As of 2026-05-25 they're documented here instead because `mas install` is broken on macOS 26.5 (requires sudo + several ADAM IDs return "No apps found"). Install via the App Store GUI — search by name, click Get/Install.

| App | ADAM ID | Notes |
|---|---|---|
| Blackmagic Disk Speed Test | 425264550 | |
| Fantastical | 975937182 | Calendar (paid) |
| GarageBand | 682658836 | |
| Harvest | 506189836 | Time tracking (paid) |
| iMovie | 408981434 | |
| Keynote | 409183694 | (Note: "Keynote Creator Studio" is a separate Apple app already on AM5; install Keynote proper only if you specifically need iWork.) |
| Meeter | 1510445899 | Auto-launches video calls. Login Item — enable in Meeter preferences. |
| NordVPN | 905953485 | Login Item — enable in NordVPN preferences. Vendor-direct download also works (https://nordvpn.com). |
| Numbers | 409203825 | See Keynote note. |
| Pages | 409201541 | See Keynote note. |
| Paprika Recipe Manager 3 | 1303222628 | Paid app. |
| Shazam | 897118787 | |
| The Unarchiver | 425424353 | |

Slack was previously listed here; moved to `cask "slack"` in the Brewfile on 2026-05-26 so it auto-updates without the App Store.

---

## Archived / no longer in use

Apps that were on AM2 but are NOT being brought forward to AM5. Kept here as an audit trail — if a future need surfaces, the install pointer is already documented.

Pruned 2026-05-25 during plan 0007 Phase 5 AM5 onboarding.

### AI clients
- **Copilot.app** — Microsoft Copilot desktop. Install: Microsoft Store / https://copilot.microsoft.com.

### Communication
- **Linear** — workspace task tracker. Install: https://linear.app/download.
- **GoToMeeting** — meeting client; was kept only for the rare meeting that required it. Install: https://www.gotomeeting.com.

### Productivity
- **Alfred 5** — launcher; superseded by Raycast. Install: https://www.alfredapp.com/ (Powerpack license if upgrading).
- **Sketch** — design tool; superseded by Figma. Install: https://www.sketch.com/download/mac.
- **Pencil (HTML5 mockups)** — wireframing. Install: https://pencil.evolus.vn/.

### Media / photo / video
- **Calibre** — eBook management. Install: https://calibre-ebook.com/download_osx.

### System / hardware
- **Logitech G HUB** — G-series peripheral configuration; carried a "waiting for user" driver-extension gate on AM2 and isn't needed without G-series gear. Install: https://www.logitechg.com/en-us/innovation/g-hub.html.
- **VIA (native)** — replaced by the **usevia.app** web app (see System / hardware section above). Native release: https://github.com/the-via/releases.
- **BeardedSpice** — media-key bridge to web players. Install: https://github.com/beardedspice/beardedspice.
- **Airfoil + Airfoil Satellite** — Mac → AirPlay audio streaming (paid). Install: https://rogueamoeba.com/airfoil/.
- **macFUSE** — filesystem-in-userspace; was a dependency for Transmit-style mounts. Install: https://osxfuse.github.io/.

### Editors / terminals
- **Sublime Text** — superseded by VS Code. Install: https://www.sublimetext.com/download (+ license).
- **iTerm** — superseded by Ghostty (+ Warp historically). Install: https://iterm2.com/.
- **Warp Terminal** — superseded by Ghostty. Install: https://www.warp.dev/.
- **Transmit** — FTP/SFTP client (paid); no current need. Install: https://panic.com/transmit/.

### Gaming / streaming
- **GeForce NOW** — cloud gaming. Install: https://www.nvidia.com/en-us/geforce-now/download/.

---

## Notes / things to revisit

- `ai.hermes.gateway.plist` and `com.dreamhome.sweepstakes.plist` LaunchAgents: investigate or remove before AM5 onboarding to avoid carrying cruft.
- Spark Desktop's cask was renamed `spark` → `spark-app` (note from old Brewfile); use `spark-app` if you ever cask it.
- `mas install` regression on macOS 26.5 is tracked as a life-atlas drift issue (#53); consider revisiting the Brewfile if a future Homebrew/mas release fixes it.
