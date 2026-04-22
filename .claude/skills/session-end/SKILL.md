---
description: Wrap up a life-atlas work session. Process docs/session-scratch.md into labeled GitHub issues, stage and commit, push the branch. Use when the user signals they're done, wrapping up, or stepping away — not only when they explicitly say "session end".
---

# Session End

## 1. Gather session state

Run in parallel:
- `git status --short` — uncommitted changes
- `git diff --stat` — what changed
- `git log --oneline --since="8 hours ago"` — commits this session

## 2. Process scratch file

Read `docs/session-scratch.md`. For each item:

**Categorize by specificity:**
- **Ready** — Problem is specific enough that an agent could execute without asking questions. You know what to build and when to stop.
- **Idea** — Concept exists but needs definition. Too vague for autonomous execution.
- **Needs input** — You need the user to clarify something before categorizing.

**Present to user:**
```
Session observations:

Ready (can be developed now):
  1. [item] → bug, priority/high, scraper
  2. [item] → feature, priority/medium, ui

Ideas (need definition):
  3. [item] → idea, kit-builder
  4. [item] → idea, data-model

Need your input:
  5. [item] — [specific question]
```

**User can:**
- Approve the categorization
- Answer questions to promote ideas to ready
- Say "ship it" to accept defaults
- Skip issue creation entirely

## 3. Create GitHub Issues

For each approved item, create via `gh issue create`:

**Ready issues:**
```
gh issue create --title "[title]" --label "ready,[type],[priority],[area]" --body "$(cat <<'EOF'
## Problem
[Specific problem statement — "done" should be obvious from reading this]

## Scope
- **Affects:** [files/areas/components]
- **Do NOT:** [explicit boundaries]

## Context
[Optional: related issues, technical notes]
EOF
)"
```

**Ideas:**
```
gh issue create --title "[title]" --label "idea,[area]" --body "[1-3 sentence description]"
```

## 4. Memory review

The auto-memory system at `~/.claude/projects/-Users-andrewlee-workspace-personal-life-atlas/memory/` only gains entries if Claude notices and writes in-the-moment. This step is the end-of-session catch-up pass.

Note: `MEMORY.md` for this project lives in the memory dir above, NOT in the repo. Never create a `MEMORY.md` inside this repo.

### 4a. Scan the session

Review the conversation for candidates by type:
- **user** — role, tools, preferences, domain knowledge the user revealed
- **feedback** — corrections the user made AND non-obvious choices they validated without pushback (always include *why*)
- **project** — decisions, motivations, deadlines, stakeholders (convert relative dates to absolute)
- **reference** — external systems, dashboards, channels the user pointed to

Exclude anything on the "What NOT to save" list: code patterns, file paths, git history, architecture, ephemeral task state, anything already documented in `CLAUDE.md`.

Persistent routing rules (unchanged):
- Durable pattern or rule → propose an edit to `CLAUDE.md` or a skill, not memory
- Cross-session gotcha → memory

### 4b. Check against existing memory

Read `MEMORY.md` in the memory dir. For each candidate, check whether an existing entry already covers it. If so, propose an **update** to that file rather than a new file.

### 4c. Propose to user

```
Memory candidates:

New:
  1. [user]     short title — content
  2. [feedback] short title — content (Why: …; How to apply: …)

Update:
  3. existing-file.md — change: …
```

User can approve all, cherry-pick, or reject. If nothing qualifies, say so and move on — don't invent entries.

### 4d. Write approved entries

For new entries:
- Create the `.md` file with frontmatter (`name`, `description`, `type`)
- For `feedback` and `project` types, structure body as: rule/fact, then **Why:** and **How to apply:** lines
- Append a one-line pointer to `MEMORY.md`: `- [Title](file.md) — one-line hook`

For updates: edit the existing file; refresh the `MEMORY.md` pointer only if its one-liner is now wrong.

### 4e. Light staleness audit

Read `MEMORY.md`. For each entry, flag:
- Named repo file paths that no longer exist
- Project memories dated more than 6 months ago (likely stale)

Surface flagged entries to the user: remove, update, or leave? Don't do deep verification here — that belongs in a separate periodic audit.

## 5. Handle uncommitted work

If uncommitted changes exist:
- **Ready to commit:** Stage specific files, commit on feature branch, push
- **Work in progress:** Commit with `wip:` prefix, push
- **Discard:** Confirm with user first, never discard silently

## 6. Push and clean up

- Push branch to remote if not already pushed
- Delete `docs/session-scratch.md`
- Report summary:

```
Session complete.
  Commits: [count]
  Issues created: [count ready] ready, [count ideas] ideas
  Branch: [name] → pushed to origin
```

## Critical rule

**Never skip the scratch file review.** Even if it's empty, confirm with the user: "No observations captured this session. Anything to log before closing?"
