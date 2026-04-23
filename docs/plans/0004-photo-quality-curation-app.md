# Plan 0004 — Photo quality curation app (exploration)

**Status:** Exploration — research only, no build commitment
**Issue:** — (create on session-end)
**Created:** 2026-04-22

---

## Goal

Decide whether to build — and if so, scope — a purpose-built tool for ongoing quality curation of a personal photo library. The tool would sit on top of Immich and address the gap between "everything in Immich" and "only the photos that meaningfully represent my life." Output of this plan is a go / no-go decision plus a build plan if go.

## Background

This plan was surfaced during plan 0002 Phase 2 (Immich dedup). Dedup solves redundancy — same photo appearing multiple times — but does nothing for the bigger problem: a photo library that has grown past the owner's ability to manually curate for quality, meaning, or shareability. Even after dedup, the library contains:

- Low-quality shots (blurry, closed eyes, bad exposure, accidental captures)
- Junk (screenshots, receipts, document scans, app exports)
- Low-signal volume (10 nearly-identical shots of the same subject, kept "just in case")
- The small fraction of actually memorable images buried in the noise

The owner wants this library to be **continuously curated** — not a one-time sweep, but an ongoing flow where new captures get triaged into quality tiers, and the library trends toward "only what's worth keeping" over time. Mobile-first, because that's where the owner is when they have spare minutes to prune.

## Scope of this exploration

- **In:**
  - Competitive landscape survey (see placeholder section below; filled by research agent)
  - Problem surface — what's actually painful today about personal photo libraries
  - Target experience sketch (not committed design — just enough to evaluate viability)
  - Architecture sketch — what plugs into Immich, what needs to be built from scratch
  - Differentiation hypothesis — what this tool could do that existing tools don't
  - Build / no-build decision, with cost estimate if build
- **Out:**
  - Any code
  - Detailed UI design
  - Backend implementation
  - Model selection / training
  - Decisions about distribution (self-host only vs. eventual SaaS) — premature until viability clear

## Problem surface

The owner's personal library is large enough that manual curation is not tractable. Key pain points:

1. **Quality drift**: the library grows faster than it's curated. Low-quality shots accumulate. Finding good photos gets harder over time.
2. **Junk clutter**: screenshots, receipts, and document scans are first-class citizens in the timeline alongside memories. They're easy to capture and hard to prune at scale.
3. **Burst/near-dup bloat**: "I took 8 shots to get one good one; I kept all 8." Multiplied across years, this is most of the library.
4. **Discoverability collapse**: the best photos are buried. "Show me the 20 photos from 2022 I'd want to show someone" is a question the current library cannot answer.
5. **Review friction**: the tools that exist require desktop sessions with visual review. The owner doesn't sit down to curate; they have 5-minute windows on a phone.

## Target experience (sketch)

- **Mobile-first.** iPhone, primarily — this is where capture happens and where spare-minute curation happens.
- **Swipe-based review.** Tinder-style: left = trash, right = keep, up = favorite/highlight, down = archive. One photo at a time, full-resolution, fast decisions.
- **Quality signals surfaced, not hidden.** "This photo is blurry" or "this looks like a receipt" shown inline so the decision is cheap.
- **Moments surfaced automatically.** The app should be able to say "here are 15 photos from your trip to Maine in June 2025 that I think capture the moments" and let the owner approve / refine → feeds into an auto-generated highlights album.
- **Ongoing, not batch.** New captures flow through a quality pipeline; low-quality gets flagged for review; high-quality gets tagged for highlights. Owner reviews the flags as a habit, not as a project.

## Architecture sketch (pre-decision)

**Inputs / integrations:**
- Immich API as source of truth. All reads and writes go through it. The app is a layer on top, not a replacement.
- Immich already provides: face recognition, CLIP smart search, object tagging.

**Gaps Immich does not fill (these are what the app would add):**
- Quality scoring (blur, exposure, closed eyes, composition)
- Junk classification (screenshot, receipt, document)
- Burst-group clustering + best-of-burst selection
- Event-significance scoring (which moments warrant highlight surfacing)
- Mobile-first review UX

**Candidate stack:**
- **Backend**: Python service running on UGREEN in Docker. Reads from Immich API, runs supplementary ML (OpenCV for blur, small classifiers for screenshots/receipts, face-landmark models for eyes, CLIP for composition / moment scoring), writes augmented metadata back as Immich tags.
- **Mobile app**: Native Swift (iPhone-first) OR React Native / Expo (cross-platform at some iteration cost). Hits the backend over Tailscale. No direct Immich API calls from the app — backend mediates so auth stays server-side.
- **Sync model**: one-way, backend → Immich tags. App makes decisions by reading tags + Immich metadata; writes back (trash, favorite, star rating) via Immich API.

Open architectural questions captured in **Open questions** below.

## Competitive landscape

*Researched 2026-04-22. Agent worked from training knowledge (early 2026), not live web sources — spot-check any specific product before committing to build decisions.*

### 1. Self-hosted photo managers

| Product | Self-hosted | Mobile-first | Immich-compat |
|---|---|---|---|
| Immich | yes | yes | — |
| PhotoPrism | yes | partial | no |
| LibrePhotos | yes | no | no |
| Ente | partial (E2E cloud, self-host option) | yes | no |
| Mylio Photos | no (local-first, P2P sync) | yes | no |
| Photoview | yes | no | no |

- **Immich** — Excellent ingest, face recognition, CLIP-based semantic search, "Memories" by date; missing native quality scoring, burst/near-dup clustering beyond exact hash, and a review-UI for keep/delete swipe flows.
- **PhotoPrism** — Strong tagging and TensorFlow classification; has a basic quality score (exposure/blur heuristic) and "stacks" for similar photos. Missing mobile-first review and moments surfacing beyond calendar/map.
- **LibrePhotos** — Event auto-generation, face clustering; slow development, minimal mobile, no quality scoring.
- **Ente** — E2E-encrypted; has magic search and memories, but self-host is underinvested vs. hosted. Doesn't scan for junk/blur.
- **Mylio Photos** — Local-first multi-device sync, "SpaceSaver," duplicate detection. Proprietary, not Immich-compatible, no true AI quality scoring.
- **Photoview** — Lightweight viewer; essentially no AI curation features.

**Gap in this category:** none ship a "triage this library" workflow with model-scored blur/eyes-closed/composition quality and a mobile review loop.

### 2. Consumer photo products with AI curation

| Product | Self-hosted | Mobile-first | Immich-compat |
|---|---|---|---|
| Google Photos | no | yes | no |
| Apple Photos | no (iCloud) | yes | no |
| Amazon Photos | no | yes | no |
| Microsoft Photos | no | partial | no |

- **Google Photos** — Best-in-class Memories, Highlights, Cinematic Photos; asks "archive this screenshot?" and suggests freeing space on low-quality items. Walled garden — cannot operate over an Immich library.
- **Apple Photos** — For You, Memories (iOS 18/26 refreshed with on-device LLM), Duplicates detector, auto-sorted Screenshots album. Locked to iCloud, no API to act on external libraries, no bulk pruning UX.
- **Amazon Photos** — Basic Memories; behind the others.
- **Microsoft Photos** — Weakest of the group for surfacing.

**What they can't do for a self-hosted user:** operate on files they don't host, expose quality scores as data, give the user agency to bulk-prune programmatically.

### 3. Professional / photographer culling tools

| Product | Self-hosted | Mobile-first | API available |
|---|---|---|---|
| Aftershoot | desktop app | no | no |
| Narrative Select | desktop app | no | no |
| FilterPixel | desktop app | no | no |
| Cull.ai | cloud | no | partial (enterprise) |
| Photo Mechanic | desktop app | no | no |

- **Aftershoot** — Market leader for wedding/event culling; excellent blur, closed-eyes, duplicate/burst detection, composition score. Desktop-only, per-shoot workflow, not built for 100k libraries or mobile.
- **Narrative Select / FilterPixel** — Fast AI-assisted keyboard cull, desktop-bound, no API.
- **Cull.ai** — Cloud-based, enterprise API inquiries but no documented public SDK.
- **Photo Mechanic** — Manual ingest gold standard; no AI quality scoring.

**Takeaway:** the underlying tech (blur / eyes / burst) is solved and commoditized. None are repurposable as a library-scale service, but the OSS equivalents are all available: OpenCV Laplacian blur variance, MediaPipe face-mesh eye-open detection, perceptual hashing, LAION aesthetic predictors v2/v2.5, CLIP-based quality heads.

### 4. Dedicated dedup / junk cleaners

| Product | Self-hosted | Mobile-first | Immich-compat |
|---|---|---|---|
| Gemini 2 (MacPaw) | local | no | no |
| PhotoSweeper | local | no | no |
| Duplicate Photos Fixer | local | partial | no |
| Remo Duplicate Photos Remover | local | partial | no |
| iMyFone Umate | local | no (iOS cleaner) | no |

- **Gemini 2 / PhotoSweeper** — Perceptual-hash dedup on a Mac filesystem; no quality scoring, no moments, no Immich awareness.
- **Mobile cleaners** — Focus on iOS Photos, clean up similar / screenshots; shallow AI (mostly pHash + basic blur); don't touch a server library.

**Scope vs. need:** these solve ~20% of the problem (exact/near dupes). Subjective quality, burst best-of, and moment surfacing are all out of scope.

### 5. AI-first photo startups / newer entrants (2024-2026)

| Product | Self-hosted | Mobile-first | Immich-compat |
|---|---|---|---|
| Memento (memento.photos) | no | yes | no |
| Journey | no | yes | no |
| Rewind.ai (photos feature) | partial (local index) | no | no |
| Slideshow.fm | no | yes | no |
| Lapse / 1Second Everyday | no | yes | no |

- **Memento** — AI-generated memory reels from camera roll; consumer-only.
- **Journey / Slideshow** — Auto-generate shareable recap videos; export-heavy, pruning-light.
- **Rewind** — Local index of digital life including screenshots; adjacent, macOS-only, not a photo curator.
- **Lapse / 1SE** — Capture-side "best moments" products; don't operate on existing libraries.
- **YC / recent launches** — W24-W25 batches included several "AI photo assistant" plays (Photo AI, Memo, various "Marco Polo for memories" clones). All consumer-SaaS, none self-hostable, none with Immich integration. **This space is being pitched repeatedly but no one has shipped for the self-host audience.**

### 6. Open-source tools adjacent

| Product | Self-hosted | Mobile-first | Immich-compat |
|---|---|---|---|
| digiKam | yes | no | no |
| Shotwell | yes | no | no |
| darktable | yes | no | no |
| czkawka | yes | no | no |
| imagededup (idealo) | library | — | library |
| dupeGuru | yes | no | no |

- **digiKam** — Mature desktop manager; basic quality scoring (blur/noise/compression/exposure heuristics), face tagging, geotag. Desktop-bound, heavyweight, no mobile.
- **czkawka / dupeGuru** — Fast CLI/desktop dedup; no quality dimension.
- **imagededup** — Python library, pHash/dHash/CNN-based near-dup; useful building block, not a product.
- **GitHub "photo curation"** — handful of hobby scripts; none production-grade.

### Immich plugin ecosystem

- **immich-go / immich-cli** — Batch ingest, useful for automation.
- **immich-power-tools** (community) — Bulk operations, duplicate review UX improvements. Closest existing third-party curation tooling on Immich today. **Worth auditing before build to see what's already covered.**
- **immich-ml / external ML workers** — Immich's ML container is swappable; custom CLIP or quality models can be dropped in. Most important plugin surface for anyone building in this space.

The Immich plugin ecosystem is early — no mature third-party marketplace, but the API is stable enough to build against and the community is explicitly inviting ML extensions.

### Gaps most consistently unfilled

These are what no current product delivers together — the defensible lane:

1. **Self-hosted + model-scored quality + mobile swipe-review in one product.** Every competitor has at most two of the three. **This is the core open lane.**
2. **Cross-library curation across iCloud *and* Immich.** Unaddressed — but probably out of scope given plan 0002's Immich-as-master direction.
3. **Bulk-scale triage UX.** Consumer apps surface 10 memories a day; pro tools cull a 2k-image shoot. Nothing is designed for a human to make meaningful dent in a 100k backlog in 5-minute mobile sessions (progress visibility, batch actions, "keep all like this," undo-safety).
4. **Quality scores as first-class, inspectable data.** Every closed product hides its scores. A self-hoster wants to query "show me all photos scored <0.2 from 2019" and act in bulk. No product exposes this.
5. **Moments surfacing that respects user-defined criteria.** Google/Apple Memories are black boxes. A "best of this trip / this kid / this year" that the user can tune (weights for faces, aesthetics, rarity of subject) doesn't exist in self-hosted or consumer form.

**Verdict:** the "AI surfaces your best moments" space is crowded for consumer cloud users and empty for self-hosted users. The defensible build is at the intersection of Immich's API, commoditized quality-scoring models, and a mobile-first triage UX — a space where no current product competes.

## Differentiation hypothesis (post-research)

Research confirmed all four pre-research hypotheses and surfaced a fifth. The defensible lane is the intersection of:

1. **Self-hosted, Immich-native.** Every consumer product (Google, Apple, Amazon, Microsoft) is walled. Every self-hosted manager (Immich, PhotoPrism, LibrePhotos) is missing quality scoring or mobile review. No one sits in both camps.
2. **Mobile-first pruning with full-res access.** Pro cullers are desktop (Aftershoot, Narrative); self-hosted is desktop or read-only mobile. The 5-minute-on-iPhone flow is not served anywhere.
3. **Continuous, not batch.** Consumer apps surface ~10 memories a day passively. Pro tools cull a 2k-image shoot once. Nothing is designed for an ongoing 100k-library triage habit.
4. **AI-surfaced moments, user-tunable.** Google/Apple Memories are black boxes. No self-hosted equivalent lets the owner tune weights (more family, less food, etc.).
5. **Quality scores as first-class, queryable data.** (New from research.) Every closed product hides scores. A self-hoster would want to query "show me all photos scored <0.2 from 2019" and act in bulk. Nothing exposes this.

**Verdict (from research):** the "AI surfaces your best moments" space is crowded for consumer-cloud users and empty for self-hosted users. The defensible build sits at Immich's API + commoditized quality-scoring models (LAION aesthetic v2.5, CLIP quality heads, MediaPipe face landmarks, OpenCV blur) + mobile-first triage UX.

**Caveat to verify before committing:** `immich-power-tools` (community project) is the closest existing third-party curation tooling on Immich. **Audit it before investing in build** — if it already covers the boring 40-60%, the build scope shrinks considerably.

## Open questions

- [x] Research: what's the competitive landscape, and where are the real gaps? Done 2026-04-22.
- [ ] **Audit `immich-power-tools`** — closest existing community tool on Immich; need to know what it already covers before scoping build.
- [ ] Is this genuinely a product, or a personal tool? The owner's framing is "build for myself but well enough it could be more." Decision deferred until post-research.
- [ ] Model choice for quality scoring: off-the-shelf (MediaPipe face landmarks, CLIP for composition) vs. a purpose-trained small model? Off-the-shelf is cheaper; training is a time sink that may not pay off for v1.
- [ ] Mobile stack: native Swift (best UX, iOS-only) vs. React Native (cross-platform, some UX cost). Depends on whether secondary workstation / iPad is in scope for v1 or v2.
- [ ] Authentication / API surface: where does the app get its Immich credentials? Re-use the owner's personal API key, or proxy through a dedicated backend account?
- [ ] Rating / tagging schema: what tag names and rating conventions will the app write to Immich? Needs to be stable across app versions and not conflict with manually-added tags.
- [ ] Offline behavior: app usable when Tailscale is flaky? Probably needs a local cache of pending decisions.
- [ ] iCloud / Google Photos integration — is the tool Immich-only, or does it also help the owner prune iCloud? Given plan 0002's Immich-as-master direction, probably Immich-only.

## Decision gate

This exploration ends with a go / no-go decision. Criteria for go:

1. Research confirms the differentiation hypotheses — there isn't an existing tool that covers Immich-native + mobile-first + continuous curation + AI moments.
2. The architecture sketch survives scrutiny — no showstopper (Immich API too thin, ML models too expensive to run on UGREEN, etc.).
3. The owner wants to build it. This is a personal project with potential product upside; motivation matters.

If go: this plan closes, and plan 0005 (or later) opens as the build plan.

## Status log

- 2026-04-22 — Exploration plan drafted. Research agent dispatched for competitive landscape.
- 2026-04-22 — Competitive landscape integrated. Five gaps identified; all pre-research hypotheses validated. Open: audit `immich-power-tools` before committing to build.
- 2026-04-22 — Build-commitment deferred. Owner: low conviction on building the full app. Near-term work (Immich dedup classifier + possibly a lightweight 10-at-a-time review UI) to stay in life-atlas on branch `feat/immich-dedup`; extract to its own repo only if scope outgrows "lightweight."
