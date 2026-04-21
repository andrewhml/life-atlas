# Plans

Multi-step implementation plans live here. Each plan is a single markdown file.

---

## Convention

- **Filename:** `NNNN-<short-name>.md` — four-digit zero-padded number, kebab-case name
- **Status markers** in header: `Draft`, `In Progress`, `Complete`, `Abandoned`
- **Active plans** are surfaced at session-start; look for `In Progress` in the header
- **Completed plans** stay here for reference; when the list grows long, move to `archive/`

## Scaffolding

Use `/plan-new <short-name> "<title>"` to create a new plan from the template.

## Relationship to GitHub issues

- **GitHub issues** = units of work (`ready`, `idea`, `bug`, etc.)
- **Plans** = how we're approaching a bigger piece of work that spans multiple issues or touches multiple areas

A plan may reference one or more GitHub issues in its header. A small self-contained issue doesn't need a plan — do it directly.

## Archive

When plans complete and the list gets noisy, move them into `archive/YYYY/` to preserve history while keeping the active list scannable.
