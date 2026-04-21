---
description: Process session observations into GitHub issues, stage and commit changes, push branch
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

## 4. Capture learnings (if any)

If something was learned during the session that future sessions need — a gotcha, a pattern, a quirk — route it:
- Pattern or durable rule → add to `CLAUDE.md` conventions or a skill
- One-off gotcha that future Claude sessions should recall → flag to the user; it will be saved to Claude's memory outside the repo
- Nothing to capture → skip this step

This repo has no `MEMORY.md`. Do not create one; cross-session state lives in Claude's memory system.

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
