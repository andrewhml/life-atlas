# Plan 0009 — Make life-atlas safe as a public guide

**Status:** In Progress
**planpong:** R5/10 | claude → codex | detail | 4P2 → 3P2 1P3 → 1P1 1P2 1P3 → 1P1 1P2 → 1P3 | Accepted: 12 | Rejected: 1 | +74/-0 lines | 17m 58s | Approved after 5 rounds
**Issue:** —
**Created:** 2026-05-26

---

## Goal

Restructure life-atlas so its public state is a reusable guide (the **HOW** — pattern, conventions, scripts, templates) and all personal data (the **WHAT** — device names, inventories, operational plans, family/geo references) lives in the right `~/Atlas/` subtrees per the Atlas pattern this project itself documents.

## Threat model

Two distinct categories of historical exposure, treated differently:

- **PII / personal context** (device names, family references, file inventories, paths): **accepted** as historically public. Sanitizing HEAD prevents this content from appearing in future commits, search-indexed `HEAD` snapshots, and shallow clones. Historical commits remain on `github.com/andrewhml/life-atlas` and any forks; this is an acknowledged residual exposure proportionate to a personal solo project.
- **Credentials / secrets** (API keys, tokens, passwords, private keys): **not accepted** at any depth. Phase 0 runs `gitleaks` (already brewed) against full history. Any finding triggers credential rotation at the source plus an explicit decision on whether to rewrite history for the affected commit range.

The public repo's audience is "someone reading the guide" plus "the user's future self across devices." The boundary being enforced is *don't leak personal context*, not *survive a determined attacker*.

## Private-destination trust model

`~/Atlas/` is the user's personal cloud-synced store (Google Drive backend). Not zero-trust — "private to the user across the user's own devices."

- **Sync surface:** Google Drive across the user's workstations, phone, tablet. No third-party agent access; no shared collaborators.
- **Existing segregation holds:** `~/Atlas/config/keys/` remains off-limits to Claude (secrets); `~/Atlas/docs/{identity,health,finance,legal,…}` remain off-limits (personal documents); `~/Atlas/share/` and most of `~/Atlas/workspace/` remain off-limits.
- **What this plan widens:** Claude write access to three narrow subtrees only — `~/Atlas/config/atlas/` (cross-device pattern→reference bindings and the lint deny-list), `~/Atlas/docs/gear/` (device inventory), and `~/Atlas/workspace/atlas-ops/` (operational plans). Content moved into these subtrees is *operational context*, not secrets.
- **Backup posture:** Atlas is included in normal user backups (NAS Time Machine, CCC mirrors). Moved content inherits that posture — no new risk surface introduced.

## Scope

- **In:** structural split of existing content between the public repo and `~/Atlas/`; templates + binding indirection; lint + pre-commit enforcement; CLAUDE.md/README sanitization; boundary updates in `.claude/settings.json`; pre-migration secret scan of full history.
- **Out:** rewriting git history for PII (already-public; deliberate acceptance per threat model); writing new public *guide* content distilled from past plans (follow-up work); changing the Atlas pattern itself; broader `~/Atlas/docs/*` lowercase migration (user-managed independently of this plan; this plan assumes a lowercase `~/Atlas/docs/gear/` exists by Phase 1 step 2).

## Target state

### Public `life-atlas/` (HOW)

```
life-atlas/
├── .claude/                          # Skills, commands, settings
├── CLAUDE.md                         # Pattern + conventions
│                                     # — "Reference implementation" table REMOVED
├── README.md                         # Pattern + role table + getting-started
│                                     # — "Reference implementation" examples REMOVED
├── folder-schemas/                   # Already abstract
├── device-schemas/
│   ├── README.md                     # Inventory shape reference; where the
│   │                                 # filled-in copy lives (~/Atlas/docs/gear/)
│   └── inventory.template.yaml       # Single file showing every field with
│                                     # placeholder values. No per-device .md
│                                     # templates — the yaml IS the schema.
├── environment/                      # Brewfile + scripts + apps-manual.md
│                                     # — Employer/personal WHY comments scrubbed
├── bookmarks/                        # Already strategy-only
├── docs/plans/                       # ONLY meta-plans about the public guide
│   ├── README.md
│   └── 0009-public-private-boundary.md   # this plan (sanitized in Phase 5)
└── scripts/
    ├── lint-no-personal-data.sh      # NEW — generic engine; reads deny-list
    │                                 #   from ~/Atlas/config/atlas/lint-denylist.txt
    ├── lint-denylist.example.txt     # NEW — generic template; show format
    └── install-hooks.sh              # NEW — symlinks lint into pre-commit hook;
                                      #   idempotent; runs after every fresh clone
```

### Private `~/Atlas/` (WHAT)

```
~/Atlas/
├── config/atlas/                     # NEW subtree under existing config/
│   ├── reference-implementation.md   # Bindings: which physical device IS the
│   │                                 # NAS, primary workstation, etc.
│   └── lint-denylist.txt             # Real token deny-list for the lint engine;
│                                     # private; cloud-synced across user devices.
├── docs/gear/                        # EXISTING category (renamed to lowercase
│   │                                 # as part of broader docs/* lowercase
│   │                                 # migration the user handles manually)
│   └── inventory.yaml                # SINGLE source of truth for device context.
│                                     # Replaces both the old inventory.yaml AND
│                                     # the 8 per-device .md files. Rich schema:
│                                     # identity, role, hardware, os, network,
│                                     # sync membership, identifiers (serials,
│                                     # MACs), free-text `notes:` per device for
│                                     # narrative content. Designed to be a
│                                     # consumable AI-context source — see the
│                                     # follow-up cross-tool device-context skill.
└── workspace/atlas-ops/              # NEW subtree under existing workspace/
    └── plans/                        # plans 0001–0008 move here (kept as
        │                             # personal execution logs)
        ├── 0001-macos-environment-init-rewrite.md
        ├── 0002-data-3-2-1-consolidation.md
        ├── 0003-zsh-prompt-setup.md
        ├── 0004-photo-quality-curation-app.md
        ├── 0005-photo-project-lifecycle.md
        ├── 0006-photo-coverage-and-icloud-drain.md
        ├── 0007-am5-onboarding-and-harness-sync.md
        └── 0008-display-config-sync.md
```

### Boundary changes for Claude (`.claude/settings.json`)

Current state (verified): `settings.json` permits writes only on `.claude/*` and `docs/*` — no Atlas rules at all. CLAUDE.md *describes* a broader Atlas write boundary ("anywhere under `~/Atlas/config/` except `keys/`"), but the settings file has never been updated to match. This plan reconciles the two — CLAUDE.md is the spec; settings.json catches up. Per the user's "spec-first" preference, the codified spec wins; settings.json is the implementation that drifted.

Grants this plan adds (narrowly scoped — only what's actually needed):

- **Atlas (private):**
  - `Write(${HOME}/Atlas/config/atlas/*)` — the new subtree only. Rest of `~/Atlas/config/` stays no-access; `keys/` segregation remains a structural guarantee (no allow rule covers it) rather than a fragile "deny below an allow."
  - `Write(${HOME}/Atlas/docs/gear/*)` — new subtree only; rest of `~/Atlas/docs/` stays no-access.
  - `Write(${HOME}/Atlas/workspace/atlas-ops/*)` — new subtree only; rest of `~/Atlas/workspace/` stays no-access.
- **Repo (public):** see Phase 1 step 3 for repo-side additions (`CLAUDE.md`, `README.md`, `device-schemas/*`, `environment/*`, `scripts/*`).

### How Claude learns the bindings post-move

Add to CLAUDE.md's "Permissions & constraints" section: bindings between the abstract Atlas pattern and the user's concrete devices (which physical box IS the NAS, etc.) live in `~/Atlas/config/atlas/reference-implementation.md`. Claude reads it on demand when a task needs a specific name. No session-start auto-load.

## Approach

### Phase 0 — Pre-migration secret scan

**Goal:** Confirm no credentials/secrets are in git history before declaring the public-history posture acceptable.

**Steps:**
1. **Tool preflight.** Verify `gitleaks` and `yq` are installed (they're in the Brewfile, but a fresh clone may not have run `brew bundle` yet). If the rewrite branch may be taken (i.e., findings expected): also verify `git-filter-repo`. Not in Brewfile today — install just-in-time with `brew install git-filter-repo` and add a permanent line to the Brewfile during Phase 3.
2. `git fetch --all --prune --tags` to ensure every remote branch and tag is present locally — `gitleaks` only sees local refs; missing remote-only refs would silently escape the scan.
3. Record the set of refs that will be scanned: `git for-each-ref --format='%(refname)' refs/heads refs/remotes refs/tags > /tmp/0009-refs-scanned.txt`. Attach the file (or its contents) to the Status log entry for traceability.
4. Run `gitleaks detect --source . --log-opts="--all"` against full history (all branches, all commits, all tags). Repo does not use git-LFS (no `.gitattributes` LFS config), so blob-level coverage is sufficient.
5. For each finding: rotate the credential at its source (revoke and reissue), then decide per finding whether to rewrite history for that commit range using `git filter-repo --replace-text`. Rotation is mandatory; history rewrite is optional and depends on the secret's blast radius.
6. Document findings + decisions in the Status log

**Exit criteria:** `gitleaks` exits clean against the recorded ref set OR every finding has a logged rotation + history-decision entry. PII-class hits are out of scope (covered by the accepted-history posture in the threat model).

### Phase 1 — Scaffold private homes + open Claude boundaries

**Goal:** All destination paths exist; Claude can write to them.

**Assumption:** the user has independently lowercased the relevant `~/Atlas/docs/*` siblings (broader docs-tree casing migration is out of scope per the Scope section). This plan only requires `~/Atlas/docs/gear/` to exist as lowercase.

**Steps:**
1. **Preflight casing check.** Before any `mkdir`, run `ls -1 ~/Atlas/docs/ | grep -i '^gear$'`. If both `Gear` and `gear` appear (possible on a case-sensitive filesystem, though both of user's primary FSes — APFS and NTFS — default to case-insensitive), stop and require a manual resolve. If only one appears, ensure it's lowercase before proceeding.
2. Create `~/Atlas/config/atlas/`, `~/Atlas/docs/gear/` (idempotent — no-op if already lowercase from step 1), `~/Atlas/workspace/atlas-ops/plans/`
3. Update `.claude/settings.json` — current allowlist (verified) permits writes only on `.claude/*` and `docs/*`. Add all of the following rules:
   - **Repo-side** (writes the plan needs in Phases 2–4): `Write(CLAUDE.md)`, `Write(README.md)`, `Write(device-schemas/*)`, `Write(environment/*)`, `Write(scripts/*)`
   - **Atlas-side** (private destinations): `Write(${HOME}/Atlas/config/atlas/*)`, `Write(${HOME}/Atlas/docs/gear/*)`, `Write(${HOME}/Atlas/workspace/atlas-ops/*)`
   - Do NOT add a blanket `~/Atlas/config/*` rule — keeping `keys/` segregation as the absence-of-allow guarantee is structurally safer than allow-then-deny.
   - Without this step, every Phase 2/3/4 edit would hit a permission gate.
4. Update CLAUDE.md to (a) document the new boundaries (Atlas + expanded repo paths), (b) document the bindings-file pointer, (c) reflect any updated docs/* casing in the Atlas-pattern section if the user's manual rename has landed

**Exit criteria:** preflight clean; new dirs exist; both Atlas-side and repo-side write boundaries open; CLAUDE.md updated.

### Phase 2 — Migrate content out of repo

**Goal:** No personal data in `CLAUDE.md`, `README.md`, `device-schemas/`, or `docs/plans/` at HEAD.

**Steps:**
1. Extract the "Reference implementation" table from `CLAUDE.md` and the parallel section from `README.md` → merge into `~/Atlas/config/atlas/reference-implementation.md`. Leave a one-line pointer in each.
2. Design the enriched device-inventory schema (single yaml, per-device records). Conceptual fields: `id` (kebab-case), `name`, `role` (primary-workstation | secondary-workstation | company-workstation | nas | mobile-phone | mobile-tablet | external-storage), `os`, `hardware` (model/year/cpu/ram/storage/gpu), `network` (hostname/ip/mac), `sync` (cloud-drives/mounted-volumes), `identifiers` (serials — private only), `notes` (free-text markdown for narrative content). Final schema iterated during execution.
3. Merge the 8 `device-schemas/*.md` files + existing `device-schemas/inventory.yaml` into a single enriched `~/Atlas/docs/gear/inventory.yaml`. Per-device `notes:` fields capture narrative content that doesn't fit structured fields.
4. **Migration checkpoint (before any deletion).** (a) Write a small manifest at `~/Atlas/docs/gear/.migration-manifest-0009.md` listing each source `.md` file with the destination device `id` and a one-line summary of what content moved into the `notes:` field. (b) Validate the merged yaml parses: `yq '.' ~/Atlas/docs/gear/inventory.yaml > /dev/null`. (c) Diff-check: for each source `.md`, confirm every non-trivial paragraph appears (verbatim or paraphrased) somewhere in the new yaml. Originals remain recoverable via `git checkout HEAD~1 -- device-schemas/<name>.md` after deletion, so git history is the snapshot — no separate staging copy needed.
5. Only after the checkpoint passes: delete the 8 `.md` files from the repo. Move only the enriched yaml, not the originals.
6. Create `device-schemas/inventory.template.yaml` showing the schema with placeholder values. No per-device `.md` templates — the yaml IS the schema.
7. Rewrite `device-schemas/README.md` to document the inventory schema, the rationale (single source of truth for AI-context use cases, like the Brewfile pattern), and where the filled-in copy lives (each user's own `~/Atlas/docs/gear/inventory.yaml`).
8. Move plans `0001-..0008-*.md` → `~/Atlas/workspace/atlas-ops/plans/`
9. Rewrite `docs/plans/README.md` to scope `docs/plans/` to meta-plans about the public guide itself
10. Walk audit output: fix or remove cross-references that pointed at the moved/deleted files

**Exit criteria:** the denied tokens (device codenames, user email, user-home path, employer name — full list lives at `~/Atlas/config/atlas/lint-denylist.txt`, see Phase 4) do not appear in `CLAUDE.md`, `README.md`, `device-schemas/`, or `docs/plans/` — with the temporary exception of `0009-public-private-boundary.md` (this plan), which still enumerates them at this point. That exception closes in Phase 5 step 2 when the plan is sanitized in-place.

### Phase 3 — Sanitize `environment/`

**Goal:** `environment/` reads as generic tool-setup content without employer or personal-project leakage.

**Steps:**
1. Brewfile: scrub WHY comments that reference employer projects (the WeasyPrint block currently names `syntheus`; rewrite as "for PDF pipelines that need WeasyPrint native libs at `/opt/homebrew/lib`")
2. Brewfile: add `brew "git-filter-repo"` under CLI: security / secrets, alongside the existing `gitleaks` line. Makes the Phase 0 rewrite path permanently available on every device.
3. `apps-manual.md`: keep install pointers (the app choices themselves aren't personal data); strip commentary that ties to personal usage patterns
4. Walk the rest of `environment/` (scripts and `*.md`) for the same scrub pass

**Exit criteria:** lint passes against `environment/`; Brewfile includes `git-filter-repo`.

### Phase 4 — Install lint + pre-commit

**Goal:** Future personal-data leakage is mechanically blocked at commit time.

**Critical design constraint:** the committed lint script must NOT itself enumerate the personal tokens. Doing so would publish at HEAD the exact list of names the plan is trying to keep out of HEAD — defeating the goal. Solution: load the real deny-list from a private path that syncs across devices via Atlas (`~/Atlas/config/atlas/lint-denylist.txt`); commit only the engine and an example template.

**Steps:**
1. Write `scripts/lint-no-personal-data.sh` — the engine only, NO real tokens:
   - Bash, no external deps beyond `grep` and `git`
   - Loads the deny-list from `${LINT_DENYLIST:-$HOME/Atlas/config/atlas/lint-denylist.txt}` (env-var override for testing; default is the synced Atlas path)
   - If the deny-list file is missing, exits nonzero with a clear error telling the user where to put it (and to seed it from `scripts/lint-denylist.example.txt`)
   - **Deny-list lines are raw regex** — the engine passes them straight to `grep -E` without wrapping. The engine does NOT auto-add word boundaries (which would silently fail for path-style tokens like `/Users/...` where `/` is not a word character). Deny-list authors are responsible for writing the right pattern for the token shape. The example template (step 2) demonstrates both common shapes.
   - Comment lines (`#`) carry rationale.
   - Greps the working tree (or staged diff in hook mode); exits nonzero on hit with file:line output
   - No exemption list needed — the script itself contains no tokens, and after Phase 5 step 2 this plan won't either.
2. Write `scripts/lint-denylist.example.txt` — committed template showing the file format with placeholder/categorical entries grouped by token shape:
   - **Word-like tokens** (codenames, hostnames) — author wraps explicitly: `\bEXAMPLE_NAS_NAME\b`, `\bEXAMPLE_WORKSTATION_TAG\b`
   - **Path-like tokens** (user-home, mount points) — no word boundary, just escaped literals: `/Users/EXAMPLE_USER`, `/Volumes/EXAMPLE_VOLUME`
   - **Email-like tokens** — escape the dot: `example\.user@example\.com`
   - Comment headers explain the shape distinction so the future user adding a new token picks the right form.
3. Create the real `~/Atlas/config/atlas/lint-denylist.txt` with the actual tokens (device codenames, user email, user-home path, employer name, family/geo tokens identified during execution). This file is private; Atlas syncs it across the user's devices.
4. Write `scripts/install-hooks.sh` — idempotent symlink (or copy) from `scripts/lint-no-personal-data.sh` to `.git/hooks/pre-commit`. Also verifies the private deny-list exists at the expected path; warns (not fails) if missing, since the lint itself will error out clearly on first run.
5. Update CLAUDE.md "Permissions & constraints" section to instruct: "After cloning life-atlas on a new device, run `bash scripts/install-hooks.sh`. The real deny-list lives at `~/Atlas/config/atlas/lint-denylist.txt` (cloud-synced via Atlas) — confirm it's present before relying on the hook."
6. Run `bash scripts/install-hooks.sh` locally on the current workstation
7. Iterate the lint until it passes against HEAD (note: this plan file still enumerates tokens at this stage — Phase 5 step 2 sanitizes it; until then, the lint will hit on this file, which is the signal Phase 5 hasn't run yet)

**Exit criteria:** `scripts/lint-no-personal-data.sh` contains no personal tokens (engine only); `scripts/lint-denylist.example.txt` is generic; the real `~/Atlas/config/atlas/lint-denylist.txt` exists and contains the live tokens; `bash scripts/install-hooks.sh` is committed and idempotent; CLAUDE.md mentions the post-clone hook install step + private deny-list location; **two deliberate test commits are blocked** — one containing a word-like deny-list token (e.g., a device codename) and one containing a path-like token (e.g., the user-home path). The path-like test specifically guards against the word-boundary failure mode the lint design avoids.

### Phase 5 — Verify + close

**Goal:** Repo is publicly coherent, this plan no longer leaks tokens, and the new model is documented.

**Steps:**
1. Run `/audit` for broken cross-references after all the moves
2. **Sanitize this plan file in-place.** Replace every specific token enumeration with categorical descriptions: device codenames → "the user's device codenames (in the private deny-list)"; specific user email → "the user's email"; `/Users/andrewhml` → "the user-home path"; employer name → "the user's employer name". Goal: the plan remains a useful HOW record for anyone reading the public guide, without revealing the user's specific WHAT. After this step, the lint passes against this file too — the Phase 2/4 temporary exception for `0009-public-private-boundary.md` closes.
3. Re-run `scripts/lint-no-personal-data.sh` against the full repo and confirm zero hits (including this plan file).
4. Stranger's-eye pass: read the repo top-down as if onboarding to it for the first time — does it work as a guide for someone who isn't me?
5. Flip `Status:` → `Complete`; add Status-log entry summarizing what shipped
6. Close drift issues that became moot (e.g., issues that referenced now-deleted device-schema files)

**Exit criteria:** audit clean; this plan file passes lint; repo reads as a coherent public guide; plan marked Complete.

## Risks

- **Cross-reference breakage.** Many existing docs link to `device-schemas/macbook-personal.md`, `docs/plans/0005-*.md`, etc. Phase 2 step 7 (walking audit output) is where this gets caught; budget real time for it.
- **Bindings discovery overhead for Claude.** Without the table in CLAUDE.md, Claude reads `~/Atlas/config/atlas/reference-implementation.md` on demand for any task that needs a specific device name. Slightly slower per task; acceptable for the privacy gain.
- **Lint false positives.** Tokens like `Mac` appear in legitimate prose. Mitigation: deny-list authors write the right regex shape per token — word-boundary-wrapped for word-like codenames, raw escaped literals for path/email shapes. The example template documents both.
- **Plan history loss.** Moved plans lose git history. Plans are personal execution logs, not collaborative artifacts. Pre-move history remains queryable via `git log -- docs/plans/0005-*.md` in the public repo if ever needed.
- **Narrative content loss during device .md → yaml merge.** The 8 per-device `.md` files carry quirks, history, decisions that must survive the collapse into structured yaml. Mitigation: walk each `.md` during Phase 2 step 3 and route every non-trivial paragraph into the device record's `notes:` field. Don't delete a `.md` until its content is verified in the yaml.
- **Atlas write-boundary widening.** Phase 1 grants Claude write on `~/Atlas/workspace/atlas-ops/` and `~/Atlas/docs/gear/`. Both are scoped narrowly — the rest of `workspace/` and most of `docs/` remain no-access. Justified per the private-destination trust model above.
- **Already-public PII history.** By design, this plan accepts PII in past commits as an acknowledged residual exposure (see Threat Model). The compensating control is Phase 0's secret scan: credentials are treated separately and not accepted at any depth.
- **Lint provides hygiene, not perimeter security.** The deny-list catches *known* leak vectors only; new device names, new family references, or unanticipated personal data slip through until added to the list. Mitigation: lint is one layer in a small stack — `gitleaks` (Brewfile) handles secret-class regressions; this plan's lint handles named-token regressions; commit-time review of public-repo changes catches the rest. Allowlist/review-board models were considered and rejected as over-engineered for a solo personal repo (see Threat Model on audience and stakes).
- **Local git hooks don't transfer across clones.** The pre-commit hook protects only the workstation where it's installed. Mitigation: `scripts/install-hooks.sh` is committed and idempotent; CLAUDE.md instructs the user to run it after cloning on any new device. Server-side CI enforcement (e.g., GitHub Actions running the lint on push/PR) is deferred as a follow-up — it would close the bypass gap fully but adds repo surface (workflows, CI minutes, failure-mode debugging) disproportionate to a solo personal repo. Re-evaluate if multi-author or external-contribution patterns ever apply.

## Follow-ups (captured as issues during `/session-end`)

- **Distilled public guides.** Sanitized public-guide docs (e.g., `docs/guides/zsh-prompt.md` from plan 0003, `docs/guides/display-config-sync.md` from plan 0008) — deferred. Decision: keep public guidance out of the repo until the personal system is proven viable for the user. Capture as a tracking issue, not addressed here.
- **Cross-tool device-context skill.** Expose `~/Atlas/docs/gear/inventory.yaml` as AI context across Claude.app, Codex.app, Claude Code, Codex CLI, Gemini CLI — analogous to how the Brewfile gives AI context on installed tools. Plan 0009 lands the data shape this skill will consume; the skill itself is a separate plan. Mechanism (skill-per-tool? MCP server? shared agent file?) decided when that plan is brainstormed.
- **Server-side lint CI.** GitHub Actions workflow that runs `scripts/lint-no-personal-data.sh` on push/PR, blocking merges that reintroduce denied tokens. Closes the bypass gap when commits come from a clone without the pre-commit hook installed. Deferred per the Risks section.

## Open questions

- **Lint mechanism convergence.** Standalone bash for now. Revisit later if custom gitleaks rules would replace it cleanly.
- **Final inventory.yaml schema.** Conceptual fields listed in Phase 2 step 2. Final shape iterated during execution; the public `inventory.template.yaml` is the artifact that locks the schema in.

## Status log

- 2026-05-26 — Plan drafted (brainstorming session)
- 2026-05-27 — Feedback round: collapsed 8 device `.md` files into a single enriched `inventory.yaml` (AI-context-consumable); lowercased `gear/` and added Atlas `docs/*` lowercase migration step (user-executed); captured cross-tool device-context skill as a follow-up.
- 2026-05-27 — planpong R1 (direction): added explicit Threat Model + Private-destination trust model sections (F1, F4); added Phase 0 gitleaks history scan (F1); removed broader `docs/*` lowercase migration from Phase 1 — user is doing it independently outside plan scope (F3); reframed lint risk to clarify hygiene-vs-perimeter posture and rejected allowlist as over-engineered for solo personal repo (F2).
- 2026-05-27 — planpong R2 (risk/pre-mortem): added Phase 2 migration checkpoint (manifest + `yq` parse-check + diff-check; git history is the snapshot — no separate staging copy) (F1); added `scripts/install-hooks.sh` for portable hook installation across clones + CLAUDE.md post-clone instruction; deferred CI as follow-up (F2); hardened Phase 0 with `git fetch --all --prune --tags` and ref-set recording, LFS scope noted (F3); added casing preflight to Phase 1 step 1 (F4).
- 2026-05-27 — planpong R3 (detail): **fixed P1 self-defeat** — the committed lint script no longer enumerates personal tokens; real deny-list moves to `~/Atlas/config/atlas/lint-denylist.txt` (cloud-synced), committed `scripts/lint-denylist.example.txt` is a generic template (F1). Phase 5 step 2 sanitizes THIS plan file in-place to remove token enumerations once the lint exists. Phase 1 step 3 expanded `.claude/settings.json` updates to include repo paths the plan edits (`CLAUDE.md`, `README.md`, `device-schemas/*`, `environment/*`, `scripts/*`) so Phase 2/3/4 don't hit permission gates (F2). Phase 0 step 1 added `git-filter-repo` preflight (install just-in-time if needed); Phase 3 adds it permanently to the Brewfile (F3).
- 2026-05-27 — planpong R4 (detail): **fixed P1 settings drift** — verified `.claude/settings.json` has no Atlas write rules at all (CLAUDE.md described the intent but settings.json never caught up). Boundary section + Phase 1 step 3 rewritten to explicitly add `Write(${HOME}/Atlas/config/atlas/*)`, `Write(${HOME}/Atlas/docs/gear/*)`, `Write(${HOME}/Atlas/workspace/atlas-ops/*)` — narrow per-subtree, no blanket `~/Atlas/config/*` allow that would risk `keys/` exposure (F1). Lint engine spec changed from "word-boundary handling baked in" (which silently fails for path-style tokens like `/Users/...`) to "raw regex passed to grep -E; authors pick the right shape per token"; example template grouped by shape (word-like, path-like, email-like); exit criteria require both word-like and path-like test commits to be blocked (F2).
- 2026-05-27 — planpong R5 (detail): **approved**. Doc consistency fix: trust-model summary updated to list all three widened private subtrees (`config/atlas/` added alongside `docs/gear/` and `workspace/atlas-ops/`), matching what Phase 1 step 3 actually grants.
