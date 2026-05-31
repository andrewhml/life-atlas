# AI configuration & working models

How the user's AI agents are set up and how they share memory. Pattern-language where it touches the public surface; concrete where it describes the reference implementation. Deep harness mechanics live in [`claude-setup.md`](./claude-setup.md); this file is the higher-level map of *which agents exist, what they run on, and how they share knowledge*.

Plans of record: `atlas-ops/0009` (AI memory backbone) and `atlas-ops/0010` (Obsidian vault reorganization). These live in the private ops repo, not here.

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

**Sync + backup:** Obsidian Sync (paid, E2EE) propagates the vault across all devices in real time; the always-on host holds a copy on disk and pushes scheduled git snapshots to the NAS for independent, long-history rollback (also closes the vault's offsite-backup gap).

---

## Local models (overnight)

The always-on host runs a local model server (Ollama) for batch/overnight work routed through Hermes — coding-capable model that fits the host's RAM, quantized. Interactive/daytime work uses the cloud Codex-OAuth model; the local model is for unattended churn. (Host RAM caps practical model size; see the inventory for the specific box.)

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
