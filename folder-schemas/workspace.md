# 🔨 Workspace — Folder Schema

**Workspace is a pattern, not a single path.** A workspace is "a folder that holds projects." Multiple workspaces exist across devices and contexts, differentiated by project characteristics.

---

## 📍 Roles

| Role | Where it lives (reference) | Contents | Why separate |
|---|---|---|---|
| Cloud drive workspace | `~/Atlas/workspace/` | Non-code projects (planning, writing, personal) | Fits cloud drive; shareable |
| Local code workspace | `~/workspace/` | Code repositories under version control | Binary-heavy for cloud sync |
| Company cloud workspace | Syntheus cloud drive | Consulting work | Separate company account |

Pick the right workspace for each project based on **what it is made of**, not where you happen to be when you start it.

---

## 📂 Internal Structure

Each workspace uses consistent top-level buckets:

```
workspace/
├── personal/       # Owned by the individual
└── work/           # Job / employer-related
```

The Syntheus workspace uses project-lifecycle buckets:

```
workspace/ (Syntheus cloud drive)
├── active-projects/
├── proposals/
├── resources/
├── admin/
└── internal/
```

Client work sits in subfolders under `active-projects/`.

---

## 🧭 Deciding Where a New Project Lives

Ask in order:

1. **Is it code under version control?** → local code workspace
2. **Is it for a consulting engagement?** → company cloud workspace
3. **Is it a personal project that's documents / planning / writing?** → cloud drive workspace (`personal/`)
4. **Is it work-adjacent but not code?** → cloud drive workspace (`work/`)

When unclear, prefer the cloud drive workspace — the shareable, portable default.

---

## 🚫 Anti-patterns

- Do not put code repositories inside the cloud drive workspace. Cloud drives handle `.git/` poorly; large `node_modules/` trees cause sync thrash.
- Do not duplicate a project across workspaces. Pick one; link or reference from the other.
- Do not mix personal and consulting work in one workspace root.

---

## 📝 Notes

- "Project" is whatever the owner treats as a project. A single-file script and a multi-month engagement both qualify.
- Archived projects move to `archive/` in the cloud drive, or to a dated subfolder in the code workspace.
- When context is ambiguous in conversation ("my workspace"), ask which workspace is meant.
