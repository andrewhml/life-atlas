# AI configuration & working models

How the user's AI agents are set up and how they share memory. Pattern-language where it touches the public surface; concrete where it describes the reference implementation. Deep harness mechanics live in [`claude-setup.md`](./claude-setup.md); this file is the higher-level map of *which agents exist, what they run on, and how they share knowledge*.

Plans of record live in the private **Metis** vault under `Ergon/Plans/` (`type: plan`) — e.g. `0009` (AI memory backbone) and `0010` (vault reorganization). Not in this public repo.

---

## The agents

| Agent | Runs on | Powered by | Role |
|---|---|---|---|
| **Claude Code** | primary + secondary workstation | Anthropic (this harness) | Coding, planning, repo + vault work |
| **Codex CLI** | primary + secondary workstation | OpenAI Codex via ChatGPT OAuth | Coding agent; also the engine behind Hermes |
| **Hermes** ([Nous Research](https://github.com/NousResearch/hermes-agent)) | always-on host | OpenAI Codex via OAuth (default runtime) | Autonomous agent: messaging gateway, scheduled jobs, overnight work |

The always-on host is a repurposed older laptop kept awake and reachable over the private mesh (Tailscale). It runs the Hermes gateway, a headless copy of the knowledge vault on disk, local models for overnight batch work, and a scheduled git backup of the vault.

---

## Two-tier memory

```
SHARED TIER  — the Obsidian vault (knowledge, durable, human + agent readable/writable)
   ▲
   │  every agent reads/writes its LOCAL copy; Obsidian Sync propagates to all devices
   │
PRIVATE TIER — each agent's own runtime memory (fast index / scratch that points into the vault)
   • Hermes: MEMORY.md / state.db / Honcho   • Claude: harness memory   • Codex: session state
```

- **Shared tier = the [Obsidian vault](#the-knowledge-vault).** This is where "memory built over time" lives and is shared across agents and devices.
- **Private tier stays per-agent.** Hermes's built-in memory can't be relocated; it bridges to the vault via Hermes's bundled `obsidian` skill + `OBSIDIAN_VAULT_PATH`. Claude's harness memory is already markdown-with-frontmatter (vault-shaped). Codex reads the vault from the filesystem.

**Privacy boundary:** anything an agent reads is sent to its model provider (Codex/Hermes → OpenAI; Claude → Anthropic). Obsidian's end-to-end encryption protects against the sync vendor, **not** the LLM providers. So the vault carries an explicit denylist (in its `Meta` note): journals, personal-people notes, and health notes are opt-in only — never auto-context. Secrets never go in the vault (they live in the password manager).

---

## The knowledge vault

A personal Obsidian vault is the shared memory substrate, organized with the **ACE framework** (Nick Milo's LYT model), renamed to a Greek motif but still spelling ACE:

| Folder | Headspace | Question |
|---|---|---|
| **Atlas** | Knowledge — to understand | Where would you like to go? |
| **Chronos** | Time — to focus | What's on your mind? |
| **Ergon** | Action — to act | What can you work on? |

Plus `Inbox/` (capture), `Home` (launchpad), `Meta` (operating manual + frontmatter contract + agent denylist), and `x/` (templates, attachments).

**Connective tissue over folders:** notes carry typed frontmatter — `type`, `up`/`in`/`related` edges, `maintained-by` (provenance) — so a client/country/person "space" is *assembled from relations* (Dataview + Bases), not maintained as a deep folder tree. This is what makes it navigable for both the human and an AI walking the links.

**Action system (Ergon):** `Goal (optional) ← Initiative (stateful: active/ongoing/simmering/hibernating) ← Task`. Tasks are **notes** (not checkboxes) with `status`/`priority`/`initiative`/`actor` frontmatter, rendered as a drag-drop kanban over a Base. Hermes writes task-notes into the vault when a task needs the human or materially advances a tracked initiative — provenance-stamped — while its trivial internal steps stay in its own kanban.

**Sync + backup:** Obsidian Sync (paid, E2EE) propagates the vault across all devices in real time; the always-on host holds a copy on disk and pushes scheduled git snapshots — shipped as a self-contained bundle over the mesh, so the NAS needs no git server and the backup survives appliance firmware updates — to the NAS for independent, long-history rollback, plus a private **offsite** mirror that closes the vault's offsite-backup gap.

---

## Local models — tiered

Local inference is **tiered by job weight**, so the always-on host stays low-power and stable while real GPU capability is still available on demand:

- **Always-on host (small, always loaded):** a coding model + a general-instruct model (7B-class, quantized) on a local Ollama server, for light and **privacy-sensitive** jobs that must not leave the mesh. No cloud involved.
- **GPU workstation (heavy, wake-on-demand):** a desktop with a discrete GPU runs a larger model (32B-class) as a wake-on-demand endpoint over the private mesh. It sleeps when idle and **wakes itself on a schedule** (an OS wake-timer task) for the overnight batch window, then sleeps again — so the workstation is never load-bearing for uptime, but its GPU is there when a heavy or long-context job needs it.
- **Routing (Hermes):** interactive/daytime → cloud Codex-OAuth; light/private → always-on local; heavy/long-context/overnight → GPU endpoint, falling back to the always-on small model if the GPU box is unreachable. Local endpoints bind to the **private mesh only** — never the LAN or public internet.

---

## Content processing — the librarian

A scheduled job on the always-on host keeps the vault legible to agents and turns raw captures into useful notes, in two layers:

- **Deterministic (no LLM):** materializes index/MOC content so *file-reading* agents (not just the Obsidian app, where Dataview renders live) see fresh results; flags sync-conflict files; runs orphan and provenance audits — **report-only** (a raw file scan can't see all reachability, so it proposes, it doesn't act).
- **Local-LLM content:** processes notes carrying a tri-state `processed` field (`pending` → dated when done; private tiers default to opt-in). It writes faithful, schema-constrained summaries and extracted action items **into the note's own sections**, stamps provenance (`maintained-by` + model tag), and **never destroys the raw note**. The model's instructions and output contract live in a versioned vault note, refined over time.
- **Privacy-preserving orchestration:** the cloud-backed agent (Hermes) schedules and routes by passing file *pointers* to a local-model subprocess; raw private content is read only by the **local** model and never enters a cloud context. This is what makes processing the private tiers safe.

---

## Migration in progress

Structured Life-Atlas data is being moved out of the cloud drive into clean vault Bases, as discrete agent tasks — starting with the **device/tech inventory** (today canonical in `~/Atlas/docs/gear/inventory.yaml`), then a **travel system**. The inventory-context skill and the disk-space app get repointed to the vault; cutover happens only after parity so agent context never breaks mid-flight.

---

## Pointers

- Deep harness runbook: [`claude-setup.md`](./claude-setup.md)
- Brew/native app inventory: [`Brewfile`](./Brewfile), [`apps-manual.md`](./apps-manual.md)
- NAS / backup target: [`nas-setup.md`](./nas-setup.md)
- Device inventory (source for the vault migration): `~/Atlas/docs/gear/inventory.yaml`
- Hermes: <https://github.com/NousResearch/hermes-agent> · <https://hermes-agent.nousresearch.com/docs/>
