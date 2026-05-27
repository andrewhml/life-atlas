# Plans

This directory holds **meta-plans about the public guide itself** — multi-step changes to how `life-atlas` is structured, what it documents, what conventions it codifies.

Operational plans (your own setup work, photo lifecycle, device-onboarding journals, etc.) belong in your own private cloud-drive workspace, not in this public repo. The reference implementation keeps them at `~/Atlas/workspace/atlas-ops/plans/`.

---

## Convention

- **Filename:** `NNNN-<short-name>.md` — four-digit zero-padded number, kebab-case name
- **Status markers** in header: `Draft`, `In Progress`, `Complete`, `Abandoned`
- **Active plans** are surfaced at session-start; look for `In Progress` in the header
- **Completed plans** stay here for reference; when the list grows long, move to `archive/`

## Scaffolding

Use `/plan-new <short-name> "<title>"` to create a new plan from the template.

## What counts as a meta-plan

In scope here:
- Restructuring decisions for the public repo (e.g., plan 0009 — public/private boundary)
- Changes to the Atlas pattern itself (folder schemas, device-schema conventions, sync topology)
- Tooling decisions that ship in this repo (lint scripts, hooks, audit/skill behavior)
- Documentation strategy changes (what belongs in README vs CLAUDE.md vs guides)

Out of scope (handle in your private `atlas-ops/plans/`):
- Setting up your own devices
- Migrating your own data
- Backups, photo workflows, hardware purchases, account hygiene
- Anything specific to your concrete reference implementation

## Relationship to GitHub issues

- **GitHub issues** = units of work (`ready`, `idea`, `bug`, etc.)
- **Plans** = how we're approaching a bigger piece of work that spans multiple issues or touches multiple areas

A plan may reference one or more GitHub issues in its header. A small self-contained issue doesn't need a plan — do it directly.

## Archive

When meta-plans complete and the list gets noisy, move them into `archive/YYYY/` to preserve history while keeping the active list scannable.
