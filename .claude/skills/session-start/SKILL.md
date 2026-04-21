---
description: Orient at the start of a life-atlas session. Check git state, list open GitHub issues, surface active plans in docs/plans/, initialize docs/session-scratch.md. Use when the user is beginning or resuming work on the repo, even without saying "session start" explicitly.
---

# Session Start

## 1. Check for leftover scratch file (DO THIS FIRST — not parallel with other steps)

Read `docs/session-scratch.md`. If it exists, a previous session didn't clean up:
- Show the contents to the user
- Ask: process these into issues now, or discard?
- Process or delete before continuing

If it doesn't exist, that's fine — continue to the next steps.

**Important:** Complete this step before starting steps 2-4. The Read tool errors on missing files, which cascade-cancels sibling parallel calls.

## 2. Git state (parallelize steps 2-4)

Run each command as a **separate Bash tool call** (no `&&`, `;`, or pipes — individual calls can run in parallel):
- `git status --short` — uncommitted changes
- `git branch --show-current` — current branch
- `git log --oneline -5` — recent commits
- `git stash list` — any stashed work

If on a feature branch with uncommitted changes, flag it.

## 3. Open issues

Run each as a **separate Bash call** (no chaining):
- `gh issue list --state open --label ready --limit 10`
- `gh issue list --state open --label idea --limit 5`

Summarize: X ready issues (Y high priority), Z ideas.

## 4. Active plans

Use **Glob** to find files in `docs/plans/*.md`, then **Grep** each for status indicators (`In Progress`, `IN PROGRESS`, `🚧`) in the first few lines. Do NOT use Bash `for` loops or `head` — use the dedicated tools.

If active plans found:
- Read each active plan file
- Summarize: plan name, current phase, what's done, what's next
- Flag if any plan appears stale (no recent updates but still marked active)

If no active plans: skip this section.

## 5. Orient

Present a brief status:

```
Branch: [current branch]
Uncommitted changes: [yes/no]
Ready issues: [count] ([high priority count] high)
Ideas: [count]
```

Then suggest:
- If active plan exists: "Active plan: [name] — currently in [phase]. Pick up where we left off?"
- If uncommitted changes: "You have work in progress on [branch]. Continue?"
- If high-priority ready issues: "Top priority: #[number] — [title]"
- If user seems undirected: "Want to pick up issues, triage ideas, or start something new?"

## 6. Initialize scratch file

**Path:** `docs/session-scratch.md`

First, check if the file already exists (another agent may have created it in a parallel session). If it exists and has content beyond the header, leave it alone. Only create it if it doesn't exist:

```markdown
# Session Scratch
```

This file captures observations during the session. `/session-end` processes it.
