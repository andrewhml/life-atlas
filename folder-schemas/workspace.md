# 🔨 Workspace — Folder Schema

**Workspace is a pattern, not a single path.** A workspace is "a folder that holds projects." Multiple workspaces exist across devices and contexts, differentiated by project characteristics.

---

## 📍 Locations

| Location | Contents | Reason for separation |
|---|---|---|
| `~/Atlas/workspace/` | Non-code projects (planning, writing, personal) | Fits Google Drive; shareable |
| `~/workspace/` | Code repositories managed by git | Too large / binary-heavy for Drive |
| Syntheus Google Drive | Consulting work | Separate company account |

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
workspace/ (Syntheus Drive)
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

1. **Is it code under version control?** → `~/workspace/`
2. **Is it for Syntheus / a consulting engagement?** → Syntheus Drive workspace
3. **Is it a personal project that's documents / planning / writing?** → `~/Atlas/workspace/personal/`
4. **Is it work-adjacent but not code?** → `~/Atlas/workspace/work/`

When unclear, prefer `~/Atlas/workspace/` — the cloud-synced default.

---

## 🚫 Anti-patterns

- Do not put code repositories inside `~/Atlas/workspace/`. Google Drive does not handle `.git/` well, and large `node_modules/` trees cause sync thrash.
- Do not duplicate a project across workspaces. Pick one; link or reference from the other.
- Do not mix personal and Syntheus work in one workspace root.

---

## 📝 Notes

- "Project" is whatever the owner treats as a project. A single-file script and a multi-month engagement both qualify.
- Archived projects move to `~/Atlas/archive/` (for Atlas workspaces) or a dated subfolder (for the code workspace).
- When context is ambiguous in conversation (user says "my workspace"), ask which workspace is meant.
