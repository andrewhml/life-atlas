# Plan 0007 — AM5 onboarding & cross-device harness sync

**Status:** Approved
**planpong:** R4/10 | claude → codex | detail | 2P2 1P3 → 5P2 1P3 → 3P1 1P2 1P3 → 3P3 | Accepted: 14 | +273/-0 lines | 27m 11s | Approved after 4 rounds
**Issues:** #43 (Claude config migration), #44 (gh auth on M5), #41 (NOTION_TOKEN secret remediation)
**Created:** 2026-05-25 (re-spec'd same day after research-driven pivot)

---

## Goal

Bring the new MacBook Pro (AM5) up to parity with AM2 across two independent-but-coupled outcomes:

- **Milestone A — Claude harness migration.** `~/.claude/` content (CLAUDE.md, statusline.sh, mcp.json, commands/, teams/, skills/, plugins manifest, settings.json) shared via a dedicated private git repo (`andrewhml/claude-harness`). Closes issue #43.
- **Milestone B — AM5 environment parity.** Brewfile reconciled and applied; native-app inventory captured and walked; gh authenticated. Closes issue #44.

The two milestones share onboarding context but can complete independently. If Milestone B is delayed (e.g., an app needs vendor attention), Milestone A can close on its own. Both milestones share the same Phase 5 onboarding gate but have distinct exit-criteria groups (see Exit criteria).

Establish a sustainable cross-device model for the harness: AM2 is the current source of truth; the design supports AM5-as-primary post-cutover with AM2 as occasional editor (bidirectional). life-atlas owns the documentation and runbook; the actual harness content lives in the harness repo.

**Out of scope:** display switch / KVM setup (separate plan); VS Code settings/extensions sync (issue #48); shell prompt (already done in plan 0003); Atlas as transport for Claude config (considered and rejected — see Background).

## Background

- Plan 0003 established the shell-prompt sync pattern via Atlas snapshot (copies, not symlinks), explicitly rejecting cloud-sync daemons in the critical path of shell startup.
- Issue #43 (2026-05-24) proposed a "hybrid symlink + snapshot" design routing `~/.claude/` through Atlas. This plan originally adopted that design and cleared 5 rounds of planpong review (R5 approved 2026-05-25, all 13 issues accepted).
- **Post-approval pivot.** A subsequent research pass on cross-machine harness best practices found that the dominant industry pattern for `~/.claude/` is git-as-transport with an allowlist `.gitignore`, NOT cloud-drive symlinks. Three specific findings drove the pivot:
  - **Symlinks into cloud-synced paths on macOS carry documented data-loss risks** (File Provider placeholder eviction; Drive silently dropping symlinks). The plan-0003 rationale generalizes — frequency of pain doesn't change the kind of pain. ([Macfilos: iCloud placeholder danger](https://www.macfilos.com/2017/06/09/2017-6-5-icloud-drive-the-danger-with-optimised-storage-file-placeholders/), [Google Drive forum: symbolic links not staying](https://support.google.com/drive/thread/3791960?hl=en))
  - **`settings.local.json` is Anthropic's intended per-machine override seam** — every practitioner repo gitignores it. The v1 plan synced it, contrary to Anthropic's design. ([code.claude.com/docs/en/settings](https://code.claude.com/docs/en/settings))
  - **`plugins/marketplaces/` contains binary plugin payloads** — the standard pattern is to sync `plugins/installed_plugins.json` (the manifest) and reinstall on each machine. ([LaPlante: Version-Controlling Your .claude Directory](https://michaellaplante.com/blog/2026-04-04-version-controlling-your-claude-directory-across-machines/))
- Practitioners converged on: a **private GitHub repo as the source of truth**, cloned into `~/.claude/` on each machine, with a `claude` shell wrapper that runs `git pull --rebase --autostash` before launching. ([elizabethfuentes12/claude-code-dotfiles](https://github.com/elizabethfuentes12/claude-code-dotfiles))
- Existing `~/.claude/skills/*` symlinks into `~/Atlas/config/ai/claude-skills/skills/` predate this pivot. They are unwound as part of Phase 2 — content moves into the new repo; the Atlas path is deprecated.
- Open issue #41 ("Investigate possible NOTION_TOKEN secret in `~/Atlas/config/ai/.mcp.json`") is folded into Phase 2a: secret audit + remediation of the legacy Atlas `.mcp.json` regardless of harness transport choice.
- `environment/Brewfile` (PR #40) is a minimal starter; reconciliation from `brew bundle dump` is part of this plan (unchanged from v1).
- **life-atlas remains the index that ties everything together** — documentation, runbook, plans, device-schema entries. The harness repo holds the content; life-atlas explains where it lives and how to operate it. This preserves the existing separation of concerns (life-atlas = docs + setup scripts about the system; the actual data lives wherever makes sense for that domain — Atlas for documents, git for code-shaped harness).

## Current state

**Confirmed on AM2 (this session, host=`AM2`, M2 Pro):**

- `~/.claude/skills/` contains 7 symlinks into `~/Atlas/config/ai/claude-skills/skills/` (contract-review, docx, pdf, pptx, session-end, session-start, xlsx)
- `~/.claude/` contains a mix of user-authored content and runtime files (categorized in Sync model section)
- `~/.claude/settings.local.json` does NOT exist
- `~/Atlas/config/ai/.mcp.json` exists (210 B, 2026-02-03), subject of issue #41
- `environment/Brewfile` exists but is minimal; needs reconciliation

**Confirmed on AM5:**

- life-atlas repo cloned (project-level `.claude/` in this repo is present)
- Global `~/.claude/` not yet populated
- macOS in default app state; Brewfile not yet run

---

## Sync model

### Architecture

- **Source of truth:** private GitHub repo `andrewhml/claude-harness`.
- **Transport:** git.
- **Working tree on each machine:** `~/.claude/` is a git clone of `andrewhml/claude-harness`.
- **No cloud-sync daemon in the critical path of Claude startup.** Drive is not involved in Claude harness sync. (Drive remains the transport for `~/Atlas/` documents and the shell-prompt snapshots from plan 0003.)
- **Atlas role for Claude:** none going forward. `~/Atlas/config/ai/claude-skills/` is deprecated and removed in Phase 2. `~/Atlas/config/ai/claude/` is never created.

### Repo layout (`andrewhml/claude-harness`)

```
.
├── CLAUDE.md                       # user global instructions
├── statusline.sh                   # statusline script
├── mcp.json                        # MCP server registry (secret-audited)
├── mcp-wrappers/                   # per-server launch wrappers that pull secrets from Keychain
├── commands/                       # slash commands
├── teams/                          # team configs
├── skills/                         # user skills (moved from Atlas in Phase 2c)
├── plugins/
│   ├── installed_plugins.lock.json # SOLE portable source of truth: per-plugin source/version/auth/install-cmd (see Plugin reinstall manifest)
│   ├── known_marketplaces.json
│   └── blocklist.json
├── settings.json                   # user-level settings
├── secrets-manifest.txt            # list of required Keychain item names (no values)
├── .gitignore                      # explicit allowlist (see below)
└── README.md                       # one-pager: clone, wrapper, gitignore rationale
```

### `.gitignore` (allowlist pattern)

```gitignore
# Ignore everything by default
*

# Then explicitly allow harness content
!CLAUDE.md
!statusline.sh
!mcp.json
!mcp-wrappers/
!mcp-wrappers/**
!commands/
!commands/**
!teams/
!teams/**
!skills/
!skills/**
!plugins/
!plugins/installed_plugins.lock.json
!plugins/known_marketplaces.json
!plugins/blocklist.json
!settings.json
!secrets-manifest.txt
!.gitignore
!README.md

# Defense-in-depth: explicitly re-exclude known runtime / per-machine paths
plugins/cache/
plugins/install-counts-cache.json
plugins/data/
plugins/marketplaces/

# plugins/installed_plugins.json is Claude Code's native artifact but contains
# AM2-local installPath under ~/.claude/plugins/cache, machine-local project paths,
# and install timestamps. NOT portable. The portable equivalent is the sanitized
# installed_plugins.lock.json above.
plugins/installed_plugins.json
```

Rationale for explicit exclusions (despite being part of `~/.claude/`):

| Path | Reason excluded |
|---|---|
| `cache/`, `debug/`, `downloads/`, `file-history/`, `ide/`, `paste-cache/`, `session-env/`, `shell-snapshots/`, `statsig/`, `telemetry/`, `tasks/`, `todos/`, `backups/`, `.last-cleanup` | Runtime state; per-machine; write-hot |
| `history.jsonl`, `sessions/`, `projects/` | Per-machine session state; conflict-prone |
| `mcp-needs-auth-cache.json`, `stats-cache.json` | Per-machine auth/stats caches |
| `settings.local.json` | Anthropic's documented per-machine override seam |
| `plugins/cache/`, `plugins/install-counts-cache.json` | Generated machine state |
| `plugins/data/` | Plugin-managed local data; per-machine |
| `plugins/marketplaces/` | Binary plugin payloads; reinstall per-machine via the lockfile |
| `plugins/installed_plugins.json` | Contains AM2-local installPath under `~/.claude/plugins/cache`, machine-local project paths, install timestamps. NOT portable. Sanitized equivalent is `installed_plugins.lock.json` |
| `~/.claude.json` (sibling to `~/.claude/`, not inside it) | OAuth session + per-project trust grants; **never sync** |

### Conflict handling

`git pull --rebase --autostash` handles the bidirectional case. Standard git workflow; real merge tooling available for JSON/markdown conflicts. No mtime guesswork; no clobber risk if used correctly. Conflicts surface as ordinary git errors that demand user action — never silent corruption.

### `claude` shell wrapper (recommended)

A function added to `~/.zshrc` (or `~/.zprofile` for login-shell scope):

```sh
claude() {
  local out ec
  # First: hard-stop on a known-broken local state. If a previous rebase or merge is
  # still in flight, the working tree is inconsistent and Claude should not launch.
  if [[ -d ~/.claude/.git/rebase-merge || -d ~/.claude/.git/rebase-apply || -f ~/.claude/.git/MERGE_HEAD ]]; then
    printf '\033[31m[claude wrapper] BLOCKED: rebase/merge in progress in ~/.claude/.\033[0m\n' >&2
    printf '\033[31m[claude wrapper] Resolve it (cd ~/.claude && git status) before launching Claude.\033[0m\n' >&2
    printf '\033[31m[claude wrapper] To bypass intentionally: `command claude`.\033[0m\n' >&2
    return 1
  fi

  out=$(cd ~/.claude && git pull --rebase --autostash 2>&1)
  ec=$?

  if (( ec != 0 )); then
    # Quiet path: network/DNS/timeout errors are expected when offline; falling through is fine.
    if echo "$out" | grep -qE 'Could not resolve host|unable to access|Temporary failure|Network is unreachable|Connection refused|Operation timed out'; then
      :
    # Hard-stop path: rebase landed in conflict OR a partial state was created. Re-check
    # for in-progress rebase/merge after the failed pull (it may have just been created).
    elif [[ -d ~/.claude/.git/rebase-merge || -d ~/.claude/.git/rebase-apply || -f ~/.claude/.git/MERGE_HEAD ]] \
         || echo "$out" | grep -qE 'CONFLICT|Could not apply|fix conflicts|both modified|both added'; then
      printf '\033[31m[claude wrapper] BLOCKED: git pull left ~/.claude/ in conflict (exit %d):\033[0m\n' "$ec" >&2
      printf '%s\n' "$out" >&2
      printf '\033[31m[claude wrapper] Resolve manually before launching Claude. To bypass intentionally: `command claude`.\033[0m\n' >&2
      return 1
    else
      # Warn-and-proceed path: auth issue, non-FF without conflict, etc. Working tree is
      # still consistent; surfacing the warning is enough.
      printf '\033[33m[claude wrapper] git pull failed (exit %d):\033[0m\n' "$ec" >&2
      printf '%s\n' "$out" >&2
      printf '\033[33m[claude wrapper] Continuing with local working tree. Run `cd ~/.claude && git status` to investigate.\033[0m\n' >&2
    fi
  fi
  command claude "$@"
}
```

Trade-offs and behavior:

- Pulls on every invocation: ~50–200 ms when no changes, ~1 s when there are changes. Acceptable for a tool the user invokes a handful of times per session.
- **Three failure classes**, in priority order:
  1. **BLOCKED (hard-stop, exit 1, Claude does NOT launch):** rebase/merge in progress (either pre-existing from a prior session or just created by this pull), or pull output contains conflict markers. Launching Claude against a half-rebased harness would read inconsistent files — worse than not launching at all.
  2. **WARN-and-proceed (yellow, Claude launches):** auth failure, non-FF without a conflict, anything else not in the quiet or blocked sets. The harness is still consistent; the warning is visible so the user can resolve later.
  3. **QUIET (no output, Claude launches):** network/DNS/timeout. Expected offline behavior.
- No automatic push on exit. The user runs `cd ~/.claude && git add . && git commit -m "..." && git push` explicitly after harness edits. Auto-commit-on-exit was considered and rejected: brittle, hard to author meaningful commit messages, encourages noisy history.
- To bypass the wrapper entirely (e.g., to launch Claude in spite of a BLOCKED state, knowing what you're doing): `command claude` or `alias noclaude='command claude'`. The wrapper's BLOCKED warnings explicitly point at this bypass so the user has an explicit consent action — not silent override.
- The quiet-failure regex is a small constant in the wrapper. Add to it if a new genuinely-expected error pattern shows up. Resist adding patterns that would mask divergence.

### Single-writer expectation

Default expectation: AM2 is sole writer until cutover; after cutover, AM5 is sole writer. The git rebase tooling makes occasional concurrent edits **recoverable**, but they're still extra friction — push promptly after edits to minimize conflict windows.

### Plugin reinstall manifest

Claude Code's native `~/.claude/plugins/installed_plugins.json` is NOT portable: it contains AM2-local `installPath` values under `~/.claude/plugins/cache`, machine-local project paths, and install timestamps (verified on AM2 during round 3 review). Committing it as-is would leave AM5 with stale records pointing at missing AM2 cache paths.

The harness repo therefore ships `plugins/installed_plugins.lock.json` as the **sole portable source of plugin intent**. The raw `installed_plugins.json` is explicitly gitignored. Schema:

```json
{
  "plugins": [
    {
      "name": "<plugin-name>",
      "source": "marketplace | git | local",
      "marketplace": "<marketplace-name>",
      "marketplace_url": "<URL or null>",
      "marketplace_auth": "<none | github-pat | other; secret name if applicable>",
      "version": "<pinned version or 'latest'>",
      "install_cmd": "<exact command to install on a fresh machine>",
      "verify_cmd": "<optional: command Claude can run to verify the plugin loaded>"
    }
  ]
}
```

**Authoring.** Phase 2 authors this file by walking each currently-installed plugin on AM2 and recording its provenance. Local-only plugins (`source: local`) need their content committed under `plugins/data/` exception — but since `plugins/data/` is gitignored, local plugins instead live under a dedicated allowlisted path TBD if a local plugin actually exists today (defer to that case). For Phase 2 the assumption is all installed plugins come from marketplaces.

**Validation gate.** Before AM2 deprecates the legacy Atlas skill/plugin state (Phase 2j), Phase 2k smoke test validates lockfile reproducibility. The minimum bar is "at least one entry per unique `(source, marketplace, marketplace_auth)` tuple" — this catches per-pattern install failures (different marketplaces, missing auth, source-specific commands) without forcing reinstall of every single plugin. Stronger bar (recommended when feasible): every entry. The exact set is chosen at Phase 2k time based on how many distinct tuples exist.

For each entry in the validation set: uninstall the plugin, run its `install_cmd` from the lockfile, then run `verify_cmd` if present. If any validation entry fails to reproduce, the lockfile is insufficient — update the failing entry (e.g., a missing flag, wrong marketplace URL) and re-validate. Do not deprecate Atlas state until the validation set is green.

**AM5 use.** Phase 5g iterates the lockfile and runs each `install_cmd`. Failure = manual reconcile.

### Secret provisioning model

Removing a secret from the harness is half the work; the consuming MCP server still needs it on every machine. The architecture commits to one default mechanism so that "provision secrets on a new machine" is a known, repeatable step rather than tribal knowledge.

**Default mechanism: macOS Keychain.** One generic password item per secret, with a consistent naming convention.

**Naming convention:** `claude-mcp-<server-name>-<credential-purpose>`. Examples:

| Secret | Keychain item name |
|---|---|
| Notion MCP integration token | `claude-mcp-notion-token` |
| GitHub MCP personal access token | `claude-mcp-github-pat` |
| Any future MCP API key | `claude-mcp-<server>-<credential>` |

**Storage (per machine, one-time per secret):**

```sh
security add-generic-password \
  -s "claude-mcp-<server>-<credential>" \
  -a "$USER" \
  -w "<the-secret>" \
  -U  # update if exists
```

**Reference from MCP config — chosen pattern (uniform, no mixing).** Each MCP server in `mcp.json` is launched via a per-server wrapper script under `mcp-wrappers/` in the harness repo. The wrapper resolves secrets from Keychain at launch time and exports them into the server's environment. `mcp.json` invokes the wrapper, not the server directly.

Example wrapper (`mcp-wrappers/notion.sh`):

```sh
#!/usr/bin/env bash
set -euo pipefail
export NOTION_TOKEN="$(security find-generic-password -s claude-mcp-notion-token -a "$USER" -w)"
exec npx -y @notionhq/notion-mcp-server "$@"
```

Corresponding `mcp.json` entry:

```json
{
  "mcpServers": {
    "notion": {
      "command": "/Users/andrewlee/.claude/mcp-wrappers/notion.sh"
    }
  }
}
```

Why this pattern over direct `${env:VAR}` interpolation in `mcp.json`:

- Works regardless of whether Claude Code supports env interpolation in `mcp.json` (Claude Code's interpolation support is not part of this plan's verified-truth set; the wrapper pattern doesn't depend on it).
- Each wrapper is a single auditable file; secret-reference logic is co-located with the launch command.
- The wrappers are committed to the harness repo (allowlisted as `mcp-wrappers/`); only the secret values live in Keychain.

**Hard prerequisite (gate before initial commit — see Phase 2c).** Pick ONE real MCP server (Notion is the natural candidate since #41 is about its token) and prove the wrapper pattern works end-to-end on AM2: secret in Keychain, wrapper resolves it, MCP server launches via Claude, an authenticated call succeeds. If the proof fails, the secret-reference model is wrong and the plan needs revision before seeding — better to discover this on AM2 than during AM5 onboarding.

**Per-machine setup script.** life-atlas hosts `environment/setup-claude-secrets.sh` that, given a manifest of required secret names, prompts the user once per missing Keychain item and stores it. The manifest lives in the harness repo (e.g., `secrets-manifest.txt` listing item names, no values). New machine runs the script after cloning the harness; existing machines re-run only when the manifest changes.

**Verification.** Phase 5i smoke test exercises each MCP server end-to-end (not just "loads without error" — actually completes an authenticated call). If a server fails to authenticate, the wrapper or env reference is misconfigured on AM5; reinstall the specific secret via the setup script.

**Audit cadence (ongoing).** Any new MCP server added to `mcp.json` triggers: (a) the Phase 2a secret audit re-run on the harness, (b) a new entry in `secrets-manifest.txt`, (c) `setup-claude-secrets.sh` run on every machine.

---

## Phases

### Phase 1 — Build the tooling and runbook

#### 1a. Create the harness repo

On GitHub: create `andrewhml/claude-harness` as **private**, no README, no .gitignore (those come from the local seed).

```sh
gh repo create andrewhml/claude-harness --private --description "Cross-device Claude Code harness — see andrewhml/life-atlas docs/plans/0007"
```

#### 1b. Write `environment/claude-setup.md`

Runbook with five sections:

1. **Initial seeding (AM2)** — steps for Phase 2 below
2. **Clone on new device (AM5 or future machines)** — steps for Phase 5
3. **Ongoing maintenance** — when to commit/push, conflict resolution, what the wrapper does, when to `git pull` manually
4. **Multi-machine etiquette** — push promptly after edits; pull-rebase is automatic via wrapper but can be re-run manually; single-writer is preferred but the rebase tooling makes occasional concurrent edits recoverable
5. **Offline / no-network mode** — wrapper falls through; working tree continues to work; sync resumes when network returns

#### 1c. Write `environment/setup-claude-secrets.sh`

Per-machine setup script that reads a manifest of required Keychain item names and prompts the user (once per missing item) to populate each. The script lives in life-atlas (not the harness repo) so that it's documented alongside the runbook and version-controlled with life-atlas's docs.

Minimum behavior:

- Input: path to `secrets-manifest.txt` (one Keychain item name per line, `#` comments ignored)
- For each item: check `security find-generic-password -s <item> -a $USER` — if absent, prompt for value (silent input), store via `security add-generic-password -s <item> -a $USER -w <value> -U`
- Print a final summary: which items were already present, which were added, which failed (e.g., user aborted prompt)
- Idempotent — safe to re-run; only prompts for missing items

#### 1d. Document the harness in life-atlas

- Add an entry under `device-schemas/inventory.yaml` for the claude-harness repo (purpose, URL, transport, related plans). Place it under a new top-level `repos:` section if one doesn't exist, or under a sub-key on existing devices.
- Add a one-line "Claude harness lives at `andrewhml/claude-harness` — see `environment/claude-setup.md`" reference to `CLAUDE.md` and the relevant device-schema docs.
- Cross-reference in `folder-schemas/config.md` under the AI section if it exists.

### Phase 2 — Seed claude-harness from AM2

#### 2a. Secret audit (mandatory gate)

Audit **two surfaces** before any content enters the new repo:

1. **About-to-be-committed files** — every file in the harness allowlist that exists on AM2 today.
2. **Already-in-Atlas AI configs** — `~/Atlas/config/ai/` tree, including `~/Atlas/config/ai/.mcp.json` (the file named in issue #41).

```sh
# Surface 1: about-to-be-committed
SEED_FILES=(
  ~/.claude/mcp.json
  ~/.claude/settings.json
  ~/.claude/CLAUDE.md
  ~/.claude/statusline.sh
  ~/.claude/plugins/installed_plugins.json
  ~/.claude/plugins/known_marketplaces.json
  ~/.claude/plugins/blocklist.json
)
SEED_DIRS=(~/.claude/commands ~/.claude/teams ~/.claude/skills)

rg -i 'token|secret|api[_-]?key|password|bearer|authorization' "${SEED_FILES[@]}" 2>/dev/null
rg -i 'token|secret|api[_-]?key|password|bearer|authorization' "${SEED_DIRS[@]}" 2>/dev/null

# Surface 2: already-in-Atlas AI configs (the file from issue #41)
# Guarded: remediation may delete the file; rg returns exit 2 on explicit missing paths.
ATLAS_AI_TARGETS=(~/Atlas/config/ai)
[[ -f ~/Atlas/config/ai/.mcp.json ]] && ATLAS_AI_TARGETS+=(~/Atlas/config/ai/.mcp.json)
rg -i 'token|secret|api[_-]?key|password|bearer|authorization' "${ATLAS_AI_TARGETS[@]}" 2>/dev/null

if [[ -f ~/Atlas/config/ai/.mcp.json ]]; then
  echo "Legacy ~/Atlas/config/ai/.mcp.json still present — confirm rg above showed no hits."
else
  echo "Legacy ~/Atlas/config/ai/.mcp.json absent — issue #41 remediation took the delete-outright path."
fi
```

**Phase 2a is split into pre-init and post-init halves** because the rg pass and manual review run on the live filesystem before any git command, while the gitleaks scanner needs the working tree + .gitignore to filter correctly:

- **2a-pre (this section above):** rg keyword pass + manual review (below) + issue-#41 remediation. Runs on `~/.claude/` directly before any git initialization. Hard stop on findings.
- **2a-post (Phase 2f below, between git init and initial commit):** gitleaks scanner. Documented in Phase 2f.

**Manual review pass (part of 2a-pre).** Tooling doesn't catch everything. Open `mcp.json` and every file under `commands/`, `teams/`, `skills/` (and the `plugins/*.json` files) and read with secret-spotting eyes. Look for: opaque ID-shaped strings, URLs with embedded creds (`https://user:pass@host`), JSON fields with provider-specific names (`integration_token`, `client_secret`, `webhook_url` with embedded tokens, etc.).

The three-layer gate is **rg keyword pass + manual review (both 2a-pre) + gitleaks (2a-post)**, all clean, before commit. If a secret reaches the initial commit anyway, recovery requires (a) immediate rotation of the exposed credential, (b) `git filter-repo` or BFG to scrub history, (c) force-push. Easier to gate hard up front.

For each hit (from any layer):

- **Real secret** → move out of any synced path. Re-home to Keychain (`security add-generic-password`), an env var sourced from a non-synced file (e.g., `~/.secrets/<name>.env`), or a per-machine config file outside the harness allowlist. Update the consuming config to reference the new location.
- **Hardcoded machine path** (e.g., `/Users/andrewlee/...`) → leave for now; documented under Risks (username collision bullet). Flag in commit message.
- **False positive** (the word "token" used in docs) → no action.

**Issue #41 specifically.** `~/Atlas/config/ai/.mcp.json` is verified to exist on AM2 (210 B, 2026-02-03). The audit must cover this file. Remediation requires one of:

- Migrate the file's content into the new harness `mcp.json` (with secrets relocated to Keychain/env), then delete the legacy file.
- Keep the legacy file but remove all secrets from it, documenting which consumer still requires this path.
- If no consumer reads it anymore, delete it outright.

Issue #41 closes only after the legacy `.mcp.json` is either secret-free or deleted — not on the basis of the new harness `mcp.json` alone.

This step is a **hard gate**: Phase 2b does not run until both audit surfaces are clean or every hit has a documented disposition.

#### 2b. Pre-mutation backup

```sh
TS=$(date -u +%Y%m%dT%H%M%SZ)
cp -RP ~/.claude ~/.claude-pre-harness-backup-$TS
echo "Backup at ~/.claude-pre-harness-backup-$TS"
echo "Restore (if needed): rm -rf ~/.claude && mv ~/.claude-pre-harness-backup-$TS ~/.claude"
```

Hard requirement before Phase 2c. If `cp` fails (disk full, permissions, etc.), stop and investigate.

#### 2c. Prove the MCP secret-reference pattern on AM2 (gate)

Before seeding the repo, prove the chosen Keychain-via-wrapper pattern (see Sync model > Secret provisioning model) works end-to-end against a real MCP server. Notion is the natural pilot since #41 already concerns its token.

```sh
# 1. Store the secret in Keychain (one-time per machine)
security add-generic-password -s "claude-mcp-notion-token" -a "$USER" -w "<the-notion-integration-token>" -U

# 2. Author the wrapper
mkdir -p ~/.claude/mcp-wrappers
cat > ~/.claude/mcp-wrappers/notion.sh <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
export NOTION_TOKEN="$(security find-generic-password -s claude-mcp-notion-token -a "$USER" -w)"
exec npx -y @notionhq/notion-mcp-server "$@"
EOF
chmod +x ~/.claude/mcp-wrappers/notion.sh

# 3. Point mcp.json at the wrapper (rewrite the notion entry)
# 4. Restart Claude Code and verify the notion MCP server connects + completes an authenticated call
```

**Gate:** if the authenticated call fails, the secret-reference model is wrong. Stop, revise the plan (or pick a different pattern), do NOT proceed to skills unwind. If it succeeds, repeat the wrapper authoring for every other MCP server in `mcp.json` (each becomes a one-line wrapper) before continuing.

Add each Keychain item name to `~/.claude/secrets-manifest.txt`:

```
claude-mcp-notion-token
claude-mcp-<next-server>-<credential>
```

#### 2d. Unwind existing skills symlinks

Skills currently live at `~/Atlas/config/ai/claude-skills/skills/` and are symlinked into `~/.claude/skills/`. To bring them into the repo:

```sh
cd ~/.claude
for s in skills/*; do
  if [[ -L "$s" ]]; then
    target=$(readlink "$s")
    rm "$s"
    cp -R "$target" "$s"
  fi
done
```

Verify: `ls -la ~/.claude/skills/` shows directories, not symlinks.

#### 2e. Initialize the git repo

```sh
cd ~/.claude
git init -b main
# Create .gitignore from Sync model > .gitignore section above
$EDITOR .gitignore
# Verify the allowlist captures only intended content
git add . && git status -s
```

Confirm the staged file list matches the harness allowlist exactly. Any unexpected file (e.g., a runtime file slipping through) → stop, update `.gitignore`, re-stage. Do NOT commit until the staged set is clean.

#### 2f. Secret scanner gate (2a-post)

Now that git is initialized, the .gitignore is filtering, and the intended files are staged, run gitleaks against both the working tree and the staged set:

```sh
# Install once: brew install gitleaks
cd ~/.claude

# Working tree (filtered by .gitignore via --no-git)
gitleaks detect --no-git --redact --verbose

# Staged set (what's actually about to be committed)
gitleaks protect --staged --redact --verbose
```

Treat ANY finding as a hard stop. Resolve (rotate the exposed credential + relocate to Keychain per the Secret provisioning model section + update the consuming wrapper or config) before continuing. Re-run both gitleaks commands until both are clean. Do NOT proceed to Phase 2g until clean.

#### 2g. Initial commit and push

```sh
git commit -m "Initial seed from AM2 (host: $(scutil --get LocalHostName))"
git remote add origin git@github.com:andrewhml/claude-harness.git
git push -u origin main
```

#### 2h. Wire the `claude` wrapper

Add the wrapper function (from Sync model > `claude` shell wrapper) to `~/.zshrc`. Reload: `exec zsh`. Test:

```sh
type claude          # should show the function body, not just the path
claude --version     # should print Claude Code version
```

Note: this is a shell-config edit. Plan 0003's `sync-shell-config.sh` covers Atlas snapshotting of `~/.zshrc` — re-run it after this addition so the wrapper survives a fresh restore on AM5 (Phase 5e).

#### 2i. Verify

```sh
cd ~/.claude
git status                          # clean working tree
git log --oneline                   # one commit
git remote -v                       # origin pushed
ls -la                              # CLAUDE.md, commands/, skills/, etc. all regular files/dirs (no symlinks)
```

#### 2j. Deprecate the Atlas path

After Phase 2g passes:

```sh
mv ~/Atlas/config/ai/claude-skills ~/Atlas/config/ai/.claude-skills-deprecated-$TS
```

Keep for one week as a safety net. Schedule deletion after Phase 5 smoke test on AM5 passes (tracked in Exit criteria). Note: this is a destructive rename on a Drive-synced path — Drive will propagate the rename. Confirm Drive sync is green before proceeding.

#### 2k. Smoke test + backup retention

Open a fresh terminal, run `claude`. Verify:

- Wrapper runs (`git pull` happens silently if there are no remote changes; warns or blocks per the wrapper's classification if not)
- Statusline renders
- Skills load
- Commands available
- CLAUDE.md loaded
- MCP servers from Phase 2c connect and complete authenticated calls
- No file-not-found errors

**Backup retention.** Do NOT delete `~/.claude-pre-harness-backup-$TS` after the AM2 smoke test. AM2 alone can miss issues that surface only on AM5 (missing skill, hardcoded path, plugin that didn't reinstall cleanly, MCP server that worked on AM2 but not AM5 because of an unmigrated env nuance). Retain the backup until AM5 has completed Phase 5i smoke test AND has run for one week without harness-related issues. Deletion is the same gate as Phase 2j Atlas-path deletion — both happen together at the end of the safety window.

If AM2 smoke test fails: restore from the backup with the command printed in Phase 2b and investigate before retrying.

### Phase 3 — Brewfile reconciliation

#### 3a. Dump current AM2 state

```sh
brew bundle dump --file=/tmp/Brewfile.dump --describe --force
```

#### 3b. Manual merge

Open `environment/Brewfile` and `/tmp/Brewfile.dump` side by side. For each entry in the dump:

- Already in Brewfile → skip
- Useful tool/app → add under the appropriate section with a one-line comment
- Forgotten install / one-off → decide: keep installed + document, or `brew uninstall`

Preserve the section comments and the `NOT brew-managed` block at the bottom.

#### 3c. Verify

```sh
brew bundle check --verbose
```

Should report `The Brewfile's dependencies are satisfied.`

#### 3d. Commit

Single commit for the Brewfile update.

### Phase 4 — Native app inventory

#### 4a. Enumerate (multiple surfaces)

```sh
# Visible app bundles
ls /Applications/ ~/Applications/ 2>/dev/null

# App Store apps
mas list

# Login Items (apps that auto-launch)
osascript -e 'tell application "System Events" to get the name of every login item'

# LaunchAgents (background services)
ls ~/Library/LaunchAgents/ /Library/LaunchAgents/ 2>/dev/null

# Fonts (user-installed beyond system + brew casks)
ls ~/Library/Fonts/ 2>/dev/null

# Browser extensions
ls ~/Library/Application\ Support/BraveSoftware/Brave-Browser/Default/Extensions/ 2>/dev/null

# Preference panes / system extensions
ls /Library/PreferencePanes/ ~/Library/PreferencePanes/ 2>/dev/null
systemextensionsctl list 2>/dev/null

# CLI tools installed outside brew
ls ~/bin/ /usr/local/bin/ 2>/dev/null | head -50
npm list -g --depth=0 2>/dev/null
pip3 list --user 2>/dev/null
```

For each non-trivial item: parity-required (goes into `apps-manual.md`) vs AM2-only (skipped, noted).

#### 4b. Write `environment/apps-manual.md`

Categorized list of every non-brew-managed parity-required item. Format per entry:

```markdown
### App / Tool Name
- **Install:** <URL, installer path, or `mas install <id>`>
- **Purpose:** <one line>
- **Setup notes:** <login, license activation, post-install config, anything non-obvious>
```

Categories (suggested):

- **AI clients** — Claude.app, Codex.app
- **Adobe CC sub-apps** — Lightroom CC, Illustrator
- **App Store** — anything from `mas list` not in Brewfile
- **Background services & LaunchAgents**
- **Fonts**
- **Browser extensions**
- **Preference panes / system extensions**
- **CLI tools outside brew**
- **Other native installers**

#### 4c. Commit

Single commit for `apps-manual.md`.

### Phase 5 — Onboard AM5

(Executed on AM5; Phases 1–4 must be committed and pushed first.)

#### 5a. Prereqs

- Install Google Drive for Desktop (needed for life-atlas runbook + plan 0003 shell config, not for the Claude harness)
- Verify the life-atlas repo is up to date: `cd ~/workspace/personal/life-atlas && git pull`
- Verify GitHub SSH access: `ssh -T git@github.com` should print "Hi andrewhml!"
- Install brew (if not present) and ensure `gh` CLI works

#### 5b. Install brew apps

```sh
brew bundle --file=environment/Brewfile
```

#### 5c. Pre-mutation backup (if ~/.claude/ has content)

```sh
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [[ -d ~/.claude && -n "$(ls -A ~/.claude 2>/dev/null)" ]]; then
  cp -RP ~/.claude ~/.claude-pre-clone-backup-$TS
  echo "Backup at ~/.claude-pre-clone-backup-$TS"
fi
```

#### 5d. Clone the harness

```sh
if [[ -d ~/.claude && -n "$(ls -A ~/.claude 2>/dev/null)" ]]; then
  echo "~/.claude/ already populated. Reconcile manually before clone."
  exit 1
fi
rm -rf ~/.claude   # only after the above check confirms it's empty (or after manual reconciliation)
git clone git@github.com:andrewhml/claude-harness.git ~/.claude
```

#### 5e. Wire the `claude` wrapper

Add the wrapper function to `~/.zshrc` (same content as AM2's Phase 2h). If plan 0003's shell-config restore already populated `~/.zshrc` from Atlas, the wrapper should already be present — verify with `type claude`. If missing, add it manually and re-run plan 0003's `sync-shell-config.sh` on whichever Mac is now authoritative for shell config.

#### 5f. Populate Keychain secrets from manifest

Run the per-machine setup script against the manifest shipped in the cloned harness:

```sh
~/workspace/personal/life-atlas/environment/setup-claude-secrets.sh ~/.claude/secrets-manifest.txt
```

The script reads each Keychain item name from the manifest, checks whether it's already populated on AM5, and prompts the user once for each missing secret (the actual secret value is pasted in interactively, never stored on disk). For values the user doesn't have at hand (e.g., a token issued only to AM2), generating a new one + revoking the AM2 instance is the safer remediation than copying the live value.

Verify:

```sh
# All manifest entries present in Keychain.
# Matches the setup-claude-secrets.sh contract: skip blank lines and #-comments.
while IFS= read -r item; do
  [[ -z "$item" || "$item" =~ ^[[:space:]]*# ]] && continue
  security find-generic-password -s "$item" -a "$USER" >/dev/null 2>&1 \
    && echo "OK: $item" \
    || echo "MISSING: $item"
done < ~/.claude/secrets-manifest.txt
```

Hard gate before 5g: every manifest entry must be OK before plugin reinstall or MCP smoke test.

#### 5g. Install non-brew apps

Walk through `environment/apps-manual.md` top to bottom.

#### 5h. Reinstall plugins from lockfile

Read `~/.claude/plugins/installed_plugins.lock.json` (authored on AM2 in Phase 2; see Sync model > Plugin reinstall manifest) and execute each entry's `install_cmd` on AM5. Marketplace payload is intentionally NOT synced — each machine fetches its own copy via the install command. After each install, run the `verify_cmd` if present.

If a `marketplace_auth` field references a Keychain item, that item should already be populated from Phase 5f. If not, populate it before running the install.

Failure = stop, reconcile manually, update the lockfile on AM2 if the install command needs to change for cross-machine reproducibility.

#### 5i. Smoke test

```sh
claude              # wrapper does git pull, harness loads
gh auth status      # issue #44 — login if needed
brew bundle check --verbose
```

Open Claude Code in an existing project. Verify session works end-to-end. Exercise each plugin from `installed_plugins.lock.json` at least once — confirm each plugin loads and behaves as it does on AM2. (If a plugin fails: that's either a missing Keychain item from 5f or a per-machine install issue. Investigate accordingly.)

Verify each MCP server in `mcp.json` completes an authenticated end-to-end call (not just "loads without error"). Auth failures here usually mean a Keychain item is missing or the wrapper script has a typo.

After passing: `rm -rf ~/.claude-pre-clone-backup-$TS` (if it was created in 5c). The AM2 pre-harness backup (from Phase 2b) is still retained per Phase 2k's one-week-after-AM5-clean-run rule.

### Phase 6 — Cutover (when AM5 becomes primary)

No structural change — both machines are now equal git clones. Cutover is just a habit shift: AM5 becomes the primary editing surface; AM2 becomes occasional editor.

Documentation update: append a paragraph to `environment/claude-setup.md` noting the cutover date and which machine is currently primary. The wrapper and the rebase workflow handle the rest automatically.

---

## Risks / open questions

- **Network at `claude` invocation** — wrapper runs `git pull` on every launch. If GitHub is unreachable, the pull fails silently and Claude falls through to the local working tree. Acceptable: Claude still starts; user sees stale content. Mitigation: documented `command claude` bypass; consider adding a hard `git fetch --dry-run` timeout if the wrapper-pull ever becomes a noticeable hang.
- **Rebase conflicts on concurrent edits** — both machines editing the same file produces conflicts. Mitigation: git's standard merge tooling; conflicts are user-visible, never silent corruption. The runbook (`claude-setup.md` section 4) documents the resolution flow.
- **Secret leak via private repo going public** — if `andrewhml/claude-harness` is ever flipped public, forked, or accidentally pushed somewhere else, any committed secrets are exposed. Mitigations: (a) Phase 2a secret audit removes secrets before initial push; (b) ongoing — re-run the audit any time a new file type joins the allowlist; (c) enable GitHub secret scanning (free for private repos); (d) consider chezmoi+age as a future migration if encrypted secrets become load-bearing.
- **Forgetting to push** — local edits sit in the working tree until pushed. Other machine doesn't see them until `git pull`. Mitigation: discipline + occasional `cd ~/.claude && git status`. Auto-commit-on-exit was considered and rejected (brittle, noisy).
- **Hardcoded absolute paths in committed content** — `settings.json` or other files may contain `/Users/andrewlee/...` permission entries. Works as long as both Macs share that username (confirmed today on AM2; AM5 should be set up the same way). Defer to "fix when it breaks" if the username ever diverges.
- **Deprecated Atlas claude-skills path** — Phase 2h renames the path; Drive propagates the rename. After one-week safety period, delete. Risk: any stray reference to the old path during that week breaks. Mitigation: grep `life-atlas/` and `~/.claude/` for `Atlas/config/ai/claude-skills` before Phase 2h.
- **Brewfile drift** — `brew install` without updating Brewfile = silent drift. Mitigation: run `brew bundle check --verbose` periodically (issue #47 for future automation).
- **`brew bundle dump --force` clobbers comments** — always dump to `/tmp/` first; never overwrite the curated Brewfile directly. Called out in `claude-setup.md`.
- **`/resume` lost across machines** — `sessions/` and `history.jsonl` stay per-machine via .gitignore. Deliberate trade-off. If cross-machine session resume becomes a felt need, the architecture supports adding `sessions/` to the allowlist later (but expect heavy git history bloat).
- **Project-level `.claude/skills/session-end` and `session-start`** — currently deleted in working tree on life-atlas repo. User-level skills (now in claude-harness) supersede them. Confirm during Phase 2; commit the deletions in life-atlas as part of harness seed work.
- **Issue #41 legacy `~/Atlas/config/ai/.mcp.json`** — orthogonal to the harness pivot. Phase 2a remediation: migrate, strip, or delete. #41 closes only when the legacy file is secret-free or absent.
- **Wrapper interaction with plan 0003 shell config** — the `claude` function lives in `~/.zshrc`. Plan 0003's `sync-shell-config.sh` snapshots `~/.zshrc` into Atlas. Adding the wrapper means re-running plan 0003's sync to capture it. Surfaced explicitly in Phase 2f and 5e.

## Exit criteria

### Milestone A — Claude harness migration (closes issue #43)

Documentation and tooling:

- [ ] `environment/claude-setup.md` exists; documents git-transport architecture, commit/push workflow, wrapper, offline behavior, conflict resolution
- [ ] `environment/setup-claude-secrets.sh` exists; idempotent; works against a `secrets-manifest.txt` shipped in the harness repo
- [ ] `device-schemas/inventory.yaml` has an entry for the claude-harness repo
- [ ] `CLAUDE.md` references the harness repo location and the runbook

Secret hygiene:

- [ ] Phase 2a three-layer audit (rg keyword + gitleaks + manual review) clean on both surfaces; or every hit has a documented disposition
- [ ] `gitleaks` installed on AM2; both `detect --no-git` and `protect --staged` runs are clean against the harness working tree before commit
- [ ] Issue #41 closed: legacy `~/Atlas/config/ai/.mcp.json` is secret-free or absent (not on the basis of the new harness `mcp.json` alone)
- [ ] Phase 2c gate passed: chosen Keychain-via-wrapper pattern proven end-to-end against the Notion MCP server on AM2 (authenticated call succeeds)
- [ ] All MCP-server credentials live in Keychain under `claude-mcp-*` naming convention; every server in `mcp.json` invokes a wrapper under `mcp-wrappers/` rather than referencing secrets inline
- [ ] `secrets-manifest.txt` committed to the harness repo, listing every required Keychain item name

AM2 state:

- [ ] AM2: `andrewhml/claude-harness` repo exists (private); initial commit pushed
- [ ] AM2: `~/.claude/` is a clean git working tree; `git status` clean; `git remote -v` shows origin
- [ ] AM2: `claude` wrapper installed in `~/.zshrc`; `type claude` shows the function; plan 0003 sync re-run to capture the wrapper in Atlas
- [ ] AM2: pre-harness backup RETAINED until AM5 has completed Phase 5i and run for one week without harness-related issues (NOT deleted at AM2 smoke test as v1 said)
- [ ] AM2: `plugins/installed_plugins.lock.json` authored with per-plugin source/version/auth/install_cmd; raw `installed_plugins.json` is gitignored (not committed); validation set covers at least one entry per unique `(source, marketplace, marketplace_auth)` tuple — each validation entry passes uninstall + `install_cmd` + `verify_cmd`
- [ ] AM2: `~/Atlas/config/ai/claude-skills/` renamed to `.claude-skills-deprecated-<TS>`; scheduled for deletion after AM5 Phase 5 passes

AM5 state (harness-specific):

- [ ] AM5: `~/.claude/` cloned from `andrewhml/claude-harness` (Phase 5d); `claude` wrapper installed (5e)
- [ ] AM5: Phase 5f run — every entry in `~/.claude/secrets-manifest.txt` populated in Keychain; verification loop reports all OK
- [ ] AM5: every plugin in `installed_plugins.lock.json` reinstalled via its `install_cmd`, `verify_cmd` (if present) passes
- [ ] AM5: `claude` invocation loads the harness; statusline visible
- [ ] AM5: every MCP server in `mcp.json` completes an authenticated end-to-end call (not just "loads without error")
- [ ] AM5: every plugin from `installed_plugins.lock.json` exercised at least once during smoke test

Closeout:

- [ ] Issue #43 closed
- [ ] Deprecated `~/Atlas/config/ai/.claude-skills-deprecated-<TS>` deleted after AM5 has run cleanly for one week
- [ ] Milestone A marked complete; plan can either close (if Milestone B follows quickly) or remain `In Progress` for B

### Milestone B — AM5 environment parity (closes issue #44)

- [ ] `environment/Brewfile` reconciled with AM2 reality; `brew bundle check --verbose` passes on AM2
- [ ] `environment/apps-manual.md` exists; covers all 8 enumeration surfaces from Phase 4a
- [ ] AM5: `brew bundle` runs clean against the reconciled Brewfile
- [ ] AM5: `apps-manual.md` walked end to end; every parity-required entry installed
- [ ] AM5: `gh auth status` shows logged in
- [ ] Issue #44 closed

### Plan closure

- [ ] Both milestones complete; plan 0007 marked `Complete`
- [ ] Follow-up issues confirmed open or filed: VS Code sync (#48 already open), display switch sync (separate plan)
