---
description: Scaffold a new plan file in docs/plans/ using the life-atlas plan template
---

# /plan-new

Scaffold a new plan file in `docs/plans/`.

## Usage

```
/plan-new <short-name> "<title>"
```

Example:

```
/plan-new macos-init-rewrite "Rewrite macos_environment_init.sh for Atlas model"
```

## What it does

1. Glob `docs/plans/*.md` to find the next available plan number (ignore `README.md` and `archive/`). Number format: four digits, zero-padded.
2. Compute filename: `docs/plans/NNNN-<short-name>.md`.
3. Write the template below, substituting `<title>`, `NNNN`, and today's date.
4. Print the path for the user.

## Template

```markdown
# Plan NNNN — <title>

**Status:** Draft
**Issue:** #N (if applicable)
**Created:** YYYY-MM-DD

---

## Goal

One paragraph: what we're trying to accomplish and why it matters.

## Scope

- **In:** what's part of this plan
- **Out:** explicitly not part of this plan

## Approach

Phased breakdown. Each phase has a goal and exit criteria.

### Phase 1 — <name>

**Goal:** ...

**Steps:**
1. ...
2. ...

**Exit criteria:** how we know this phase is done.

### Phase 2 — <name>

...

## Risks

- What could go wrong
- What we'd need to revisit

## Open questions

- Things we don't know yet
- Decisions to make before starting

## Status log

- YYYY-MM-DD — Plan drafted
```

## Status markers

The `Status:` line in the header drives session-start behavior:

- `Draft` — written but not active
- `In Progress` — session-start will surface it
- `Complete` — work done; keep for reference
- `Abandoned` — decided not to pursue; keep for history

Session-start searches for `In Progress` or `🚧` in the first few lines.

## After scaffolding

Remind the user to:

1. Fill in the Goal and Scope
2. Link the related GitHub issue (if any) in the header
3. Flip `Status: Draft` → `Status: In Progress` when starting execution
