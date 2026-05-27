# 🗂️ Device schemas

A single yaml file documents every device in your Atlas ecosystem. The yaml IS the schema — no per-device markdown files, no separate templates for each device class.

## Why one yaml

Two reasons drove the design (see plan 0009 for the full rationale):

1. **AI-context consumability.** Modern AI assistants (Claude, Codex, Gemini, etc.) work best when domain context is compact and structured — similar to how a Brewfile lets an AI reason about your installed tools. A single grep-able, parseable yaml is a much better context source than 8 separate markdown narratives.
2. **YAGNI.** Per-device markdown templates were artifact-for-its-own-sake. The structural fields (id, role, hardware, storage, network, sync) capture everything that's queryable; a free-text `notes:` field per device holds the narrative content that doesn't fit a schema field.

## What lives where

| Surface | Path | Purpose |
|---|---|---|
| **Schema template** (public) | `device-schemas/inventory.template.yaml` | Skeleton with placeholder values. Demonstrates the shape any user fills in. |
| **Schema README** (public) | `device-schemas/README.md` | This file. |
| **Filled-in inventory** (private, per user) | `~/Atlas/docs/gear/inventory.yaml` | Your actual devices. Cloud-synced across your own devices via the cloud drive; never committed to any public repo. |

## Getting started

1. Copy `inventory.template.yaml` to `~/Atlas/docs/<your gear category>/inventory.yaml` on your primary workstation (or wherever your cloud-drive folder lives).
2. Replace the example device records with your own. Drop fields that don't apply; add fields you need.
3. Keep field names consistent across devices for the same concept so the file stays grep-friendly.
4. Update whenever capacity, services, or backup flows change. Validate with `yq '.' ~/Atlas/docs/gear/inventory.yaml > /dev/null` after edits.

## Conventions

- **Sizes in GB/TB as decimal** (1 TB = 1000 GB), matching vendor labels. Use `_bytes` suffix when bytes-exact matters.
- **`null` or `tbd`** = unknown / not yet measured. Don't guess.
- **`verified` dates** are when a human (or tool) last confirmed the value. Treat anything older than the value's volatility class as stale.
- **Cross-references** to plans, issues, runbooks → bare strings, not links.
- **Identifiers** (serials, MACs) are private. The template includes the field so the schema is complete, but never commit a filled-in inventory.yaml that contains them into any public repo.

## Cross-tool device-context skill

Plan 0009 commits to landing the data shape that a future cross-tool skill will consume — Claude.app, Codex.app, Claude Code, Codex CLI, Gemini CLI — so any AI tool you reach for can read your `inventory.yaml` and reason about your hardware before suggesting tools, purchases, or configuration changes. That skill is its own plan (see life-atlas issues for the tracking item); this file's job is to keep the data clean and parseable.
