# Claude Code harness setup

Runbook for the Claude Code harness shared across personal Macs via a private git repo. (Phase 3 will scrub the personal-repo name; for now the broken cross-link to the private plan that originally documented this is removed.)

**Architecture in one paragraph:** `~/.claude/` on each machine is a git clone of `andrewhml/claude-harness`. Edits get committed and pushed; other machines pull via a `claude` shell wrapper that runs `git pull --rebase --autostash` before launching Claude Code. Secrets live in macOS Keychain (never in the repo); MCP servers are launched via per-server wrappers under `mcp-wrappers/` that pull secrets at launch time. Per-machine runtime state (`sessions/`, `history.jsonl`, `cache/`, `settings.local.json`, etc.) is gitignored.

---

## 1. Initial seeding (AM2, one-time)

This is how the harness repo got populated from AM2 originally. Followed once; re-read here for context only.

See plan 0007 Phase 2a–2k for the authoritative steps. Summary:

1. **2a-pre — secret audit (rg + manual review)** on the live `~/.claude/` filesystem before any git command. Includes the legacy `~/Atlas/config/ai/.mcp.json` (issue #41).
2. **2b — pre-mutation backup** of the existing `~/.claude/` to `~/.claude-pre-harness-backup-<TS>/`. Retained until AM5 has run cleanly for one week.
3. **2c — prove the MCP secret-reference pattern** with one real server (Notion). Authenticated call must succeed on AM2 before seeding.
4. **2d — unwind existing skills symlinks** (replace each `~/.claude/skills/<name>` symlink with the real content).
5. **2e — `git init` + `.gitignore`** using the allowlist pattern (see [Repo layout and gitignore](#repo-layout-and-gitignore) below). Stage; verify the staged set matches the allowlist exactly.
6. **2f — gitleaks gate** (`gitleaks detect --no-git` then `gitleaks protect --staged`). Hard stop on any finding.
7. **2g — initial commit and push** to `git@github.com:andrewhml/claude-harness.git`.
8. **2h — install the `claude` shell wrapper** in `~/.zshrc` (see [The `claude` shell wrapper](#the-claude-shell-wrapper) below). Re-run plan 0003's `sync-shell-config.sh` after so the wrapper survives an AM5 zshrc restore.
9. **2i–2j — verify and deprecate** the legacy Atlas claude-skills path (`mv ~/Atlas/config/ai/claude-skills ~/Atlas/config/ai/.claude-skills-deprecated-<TS>`).
10. **2k — smoke test** + retain backup until AM5 has run cleanly for one week.

---

## 2. Clone on new device (AM5 or future machines)

Step-by-step procedure when bringing up a new Mac. Assumes you have: Google Drive for Desktop installed, life-atlas repo cloned, SSH access to your GitHub account, `gh` and `brew` installed.

```sh
# Prereq: GitHub SSH works
ssh -T git@github.com   # should print "Hi andrewhml!"

# Backup any existing ~/.claude/ (safety net for first-time onboarding)
TS=$(date -u +%Y%m%dT%H%M%SZ)
if [[ -d ~/.claude && -n "$(ls -A ~/.claude 2>/dev/null)" ]]; then
  cp -RP ~/.claude ~/.claude-pre-clone-backup-$TS
  echo "Backup at ~/.claude-pre-clone-backup-$TS"
fi

# Clone the harness
if [[ -d ~/.claude && -n "$(ls -A ~/.claude 2>/dev/null)" ]]; then
  echo "~/.claude/ already populated. Reconcile manually before clone."
  exit 1
fi
rm -rf ~/.claude
git clone git@github.com:andrewhml/claude-harness.git ~/.claude

# Install the `claude` wrapper in ~/.zshrc — see The `claude` shell wrapper section below.
# If plan 0003's shell-config restore already populated ~/.zshrc from Atlas, verify with:
type claude   # should show the function body
# If missing, add it manually.

# Populate Keychain secrets from the manifest shipped with the harness
~/workspace/personal/life-atlas/environment/setup-claude-secrets.sh ~/.claude/secrets-manifest.txt

# Verify all manifest entries present in Keychain (skip blanks + comments)
while IFS= read -r item; do
  [[ -z "$item" || "$item" =~ ^[[:space:]]*# ]] && continue
  security find-generic-password -s "$item" -a "$USER" >/dev/null 2>&1 \
    && echo "OK: $item" \
    || echo "MISSING: $item"
done < ~/.claude/secrets-manifest.txt

# Install brew apps (separate from the harness; lives in life-atlas)
brew bundle --file=~/workspace/personal/life-atlas/environment/Brewfile

# Reinstall plugins from the lockfile
# For each entry in ~/.claude/plugins/installed_plugins.lock.json, run install_cmd, then verify_cmd if present.
# (Currently manual; future enhancement: a small replay script.)

# Walk through native-app installs
$EDITOR ~/workspace/personal/life-atlas/environment/apps-manual.md

# Smoke test
claude              # wrapper does git pull, harness loads
gh auth status      # login if needed
brew bundle check --verbose
```

---

## 3. Ongoing maintenance

### Daily / per-session

Nothing required. The `claude` wrapper pulls the latest harness on every invocation. If GitHub is reachable, you're current. If not, you fall through to the local working tree (Claude still starts; see [Offline / no-network mode](#5-offline--no-network-mode)).

### After editing a skill, command, statusline, CLAUDE.md, mcp.json, or any other harness file

```sh
cd ~/.claude
git status                          # confirm what you actually changed
git add <files>                     # specific files, not -A
git commit -m "<short message>"
git push
```

The other machine will see the change on its next `claude` invocation (via the wrapper's `git pull`).

### After adding or changing an MCP server

In addition to the commit/push above:

1. If the new server uses a secret, add a wrapper under `mcp-wrappers/<server>.sh` that resolves the secret from Keychain (see `mcp-wrappers/notion.sh` as the template).
2. Add the Keychain item name to `~/.claude/secrets-manifest.txt`.
3. Re-run the Phase 2a secret audit (`rg` keyword pass + gitleaks) before committing — any new file is a new audit surface.
4. On the OTHER machine, after the next pull, run `~/workspace/personal/life-atlas/environment/setup-claude-secrets.sh ~/.claude/secrets-manifest.txt` to populate the new Keychain item.

### After installing a new plugin

Update `~/.claude/plugins/installed_plugins.lock.json` with the new entry (name, source, marketplace, marketplace_auth, version, install_cmd, verify_cmd). Commit + push. On the other machine, run the new entry's `install_cmd` after the next pull.

### Periodic

- Re-run gitleaks against the working tree quarterly: `cd ~/.claude && gitleaks detect --no-git --redact --verbose`.
- Re-run `brew bundle check --verbose` periodically; reconcile the Brewfile if drift appears.

---

## 4. Multi-machine etiquette

**Single-writer expectation.** At any given time, one Mac is the active editor. The other Mac is a consumer that pulls and reads. The git rebase tooling makes occasional concurrent edits **recoverable**, but the recovery is friction; minimize concurrent windows.

**Push promptly after edits.** Don't let local commits sit unpushed on one machine for hours while the other machine is also potentially editing. The longer the gap, the higher the chance of rebase conflict on next pull.

**Pull-rebase is automatic via the wrapper** but you can re-run it manually anytime:

```sh
cd ~/.claude && git pull --rebase --autostash
```

**If the wrapper warns about a non-network git failure** (yellow `[claude wrapper]` line on stderr), don't ignore it. Common causes:

- **Non-fast-forward / divergent edits:** the other machine pushed something you haven't pulled. Resolve: `cd ~/.claude && git pull --rebase`. If clean, you're done; if conflict, see below.
- **Auth failure:** SSH key may have rotated or been removed from GitHub. Re-add and retry.
- **Dirty working tree blocking rebase:** the autostash should usually handle this. If it didn't, `git status` will explain.

**If the wrapper BLOCKS** (red `[claude wrapper] BLOCKED:` line), Claude did NOT launch and the working tree is in a half-rebased or conflicted state. Do NOT bypass with `command claude` until you've resolved:

```sh
cd ~/.claude
git status                          # see what's conflicted
# Resolve the conflicts in the listed files (typically settings.json, mcp.json, or a skill file)
git add <resolved files>
git rebase --continue               # or `git rebase --abort` to bail
```

After resolution, retry `claude`.

**Post-cutover transition** (when AM5 becomes the primary editor):

Append a paragraph to this file noting the cutover date and which machine is currently primary. AM2 becomes the occasional editor. The wrapper handles the rebase mechanics automatically; the only behavioral change is which machine you habitually open Claude on.

---

## 5. Offline / no-network mode

When GitHub or the local network is unreachable:

- The wrapper's `git pull` fails silently (matched by the wrapper's quiet-failure regex: `Could not resolve host`, `unable to access`, `Temporary failure`, etc.).
- Claude launches against the local working tree — whatever the harness looked like at last successful pull.
- You can edit, commit locally, and push later when connectivity returns. The wrapper will pull on next invocation.

**Detection.** If you want to confirm whether the wrapper pulled or fell through:

```sh
cd ~/.claude && git log -1 --format="%h %s (%cr)"
```

The relative date tells you when the last commit landed. If it's "5 days ago" and you expect newer content, you're probably running on a stale pull because of an offline interval — manually retry:

```sh
cd ~/.claude && git pull --rebase --autostash
```

**Snapshot files (`settings.json`).** Still local files; not affected by network state. Claude reads them normally.

**Drive-paused mode** is irrelevant to the Claude harness — Drive is not in the harness sync path. (Drive being paused does affect the legacy `~/Atlas/config/ai/.claude-skills-deprecated-*` folder, but that's the safety-net copy, not active.)

---

## Repo layout and `.gitignore`

The `andrewhml/claude-harness` repo:

```
.
├── CLAUDE.md                       # user global instructions
├── statusline.sh                   # statusline script
├── mcp.json                        # MCP server registry (secret-audited)
├── mcp-wrappers/                   # per-server launch wrappers that pull secrets from Keychain
├── commands/                       # slash commands
├── skills/                         # user skills
├── plugins/
│   └── installed_plugins.lock.json # SOLE portable source: per-plugin source/version/auth/install_cmd + $marketplaces_required block
├── settings.json                   # user-level settings
├── secrets-manifest.txt            # required Keychain item names (no values)
├── .gitignore                      # explicit allowlist (see below)
└── README.md                       # one-pager: clone, wrapper, gitignore rationale
```

`.gitignore` (allowlist pattern):

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
!skills/
!skills/**
!plugins/
!plugins/installed_plugins.lock.json
!settings.json
!secrets-manifest.txt
!.gitignore
!README.md

# Defense-in-depth: explicitly re-exclude known runtime / per-machine paths
plugins/cache/
plugins/install-counts-cache.json
plugins/data/
plugins/marketplaces/

# Claude Code's native installed_plugins.json contains AM2-local installPath under
# ~/.claude/plugins/cache, machine-local project paths, and install timestamps.
# NOT portable. installed_plugins.lock.json is the sanitized equivalent.
plugins/installed_plugins.json

# teams/ holds per-project Claude Code "teams" feature conversation transcripts.
# Runtime state, same category as sessions/ and projects/.
teams/

# known_marketplaces.json + blocklist.json mix user intent with cache fields
# that churn every Claude session. Portable marketplace intent lives in
# installed_plugins.lock.json > $marketplaces_required.
plugins/known_marketplaces.json
plugins/blocklist.json
```

---

## The `claude` shell wrapper

Add to `~/.zshrc` (or `~/.zprofile` for login-shell scope):

```sh
claude() {
  local out ec
  # First: hard-stop on a known-broken local state.
  if [[ -d ~/.claude/.git/rebase-merge || -d ~/.claude/.git/rebase-apply || -f ~/.claude/.git/MERGE_HEAD ]]; then
    printf '\033[31m[claude wrapper] BLOCKED: rebase/merge in progress in ~/.claude/.\033[0m\n' >&2
    printf '\033[31m[claude wrapper] Resolve it (cd ~/.claude && git status) before launching Claude.\033[0m\n' >&2
    printf '\033[31m[claude wrapper] To bypass intentionally: `command claude`.\033[0m\n' >&2
    return 1
  fi

  out=$(cd ~/.claude && git pull --rebase --autostash 2>&1)
  ec=$?

  if (( ec != 0 )); then
    # Quiet path: network/DNS/timeout errors expected when offline.
    if echo "$out" | grep -qE 'Could not resolve host|unable to access|Temporary failure|Network is unreachable|Connection refused|Operation timed out'; then
      :
    # Hard-stop path: rebase landed in conflict OR partial state.
    elif [[ -d ~/.claude/.git/rebase-merge || -d ~/.claude/.git/rebase-apply || -f ~/.claude/.git/MERGE_HEAD ]] \
         || echo "$out" | grep -qE 'CONFLICT|Could not apply|fix conflicts|both modified|both added'; then
      printf '\033[31m[claude wrapper] BLOCKED: git pull left ~/.claude/ in conflict (exit %d):\033[0m\n' "$ec" >&2
      printf '%s\n' "$out" >&2
      printf '\033[31m[claude wrapper] Resolve manually before launching Claude. To bypass intentionally: `command claude`.\033[0m\n' >&2
      return 1
    else
      # Warn-and-proceed: auth issue, non-FF without conflict, etc.
      printf '\033[33m[claude wrapper] git pull failed (exit %d):\033[0m\n' "$ec" >&2
      printf '%s\n' "$out" >&2
      printf '\033[33m[claude wrapper] Continuing with local working tree. Run `cd ~/.claude && git status` to investigate.\033[0m\n' >&2
    fi
  fi
  command claude "$@"
}
```

Three failure classes, in priority order:

1. **BLOCKED** (red, exit 1, Claude does NOT launch): pre-existing rebase/merge in progress, or pull just created a conflict.
2. **WARN-and-proceed** (yellow, Claude launches): auth failure, non-FF without conflict, anything not in the other sets.
3. **QUIET** (no output, Claude launches): network/DNS/timeout.

To bypass the wrapper: `command claude` (one-time) or `alias noclaude='command claude'` (persistent).

---

## Secret provisioning model

**Default mechanism:** macOS Keychain. One generic password item per secret.

**Naming convention:** `claude-mcp-<server>-<credential-purpose>`. Examples:

| Secret | Keychain item name |
|---|---|
| Notion MCP integration token | `claude-mcp-notion-token` |
| GitHub MCP personal access token | `claude-mcp-github-pat` |
| Any future MCP API key | `claude-mcp-<server>-<credential>` |

**Storage:**

```sh
security add-generic-password \
  -s "claude-mcp-<server>-<credential>" \
  -a "$USER" \
  -w "<the-secret>" \
  -U
```

(`-U` updates if exists; safe to re-run.)

**Reference from `mcp.json`:** each MCP server is launched via a per-server wrapper under `mcp-wrappers/` that resolves the secret from Keychain at launch and exports it into the server's environment. The wrapper is committed; the secret value is NOT. Example wrapper (`mcp-wrappers/notion.sh`):

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

**Per-machine setup:** run `~/workspace/personal/life-atlas/environment/setup-claude-secrets.sh ~/.claude/secrets-manifest.txt` after cloning the harness on a new machine; re-run when the manifest gets a new entry.

---

## When to re-run the secret audit

Re-run Phase 2a audit any time a new file enters the harness allowlist or any new MCP server is added to `mcp.json`:

```sh
# Surface 1: harness files
cd ~/.claude
rg -i 'token|secret|api[_-]?key|password|bearer|authorization' \
  CLAUDE.md statusline.sh mcp.json settings.json \
  commands/ skills/ mcp-wrappers/ \
  plugins/installed_plugins.lock.json plugins/known_marketplaces.json plugins/blocklist.json \
  secrets-manifest.txt 2>/dev/null

# Surface 2: existing Atlas AI configs (carries forward from plan 0007 Phase 2a)
ATLAS_AI_TARGETS=(~/Atlas/config/ai)
[[ -f ~/Atlas/config/ai/.mcp.json ]] && ATLAS_AI_TARGETS+=(~/Atlas/config/ai/.mcp.json)
rg -i 'token|secret|api[_-]?key|password|bearer|authorization' "${ATLAS_AI_TARGETS[@]}" 2>/dev/null

# Layer 2: gitleaks
gitleaks detect --no-git --redact --verbose
```

Then `gitleaks protect --staged --redact --verbose` before commit.

---

## Pointers

- **Setup script:** `environment/setup-claude-secrets.sh`
- **Brewfile:** `environment/Brewfile`
- **Native app inventory:** `environment/apps-manual.md`
- **Harness repo:** `git@github.com:andrewhml/claude-harness.git` (private)
