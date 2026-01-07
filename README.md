# 🧭 Life Atlas

**Life Atlas** is a structured, device-agnostic folder and environment system designed to help you organize your digital life — consistently and intentionally.

---

## ✨ Purpose

This project helps you:

- Mirror a clear folder structure across devices (Mac, PC, NAS, mobile)
- Separate work, personal, academic, and business life cleanly
- Archive important documents (tax, legal, healthcare, IDs, etc.)
- Create and sync consistent development/creative environments
- Maintain bookmarks, setup scripts, and OS preferences

It’s your **atlas** for navigating digital life.

---

## 💻 Devices Covered

- MacBook Pro (Personal)
- MacBook Pro (Work)
- Personal PC (Windows or Linux)
- UGREEN NAS (Shared + Personal)
- iPad (2024)
- iPhone 16 Pro

---

## 🗂 Folder Structure (Overview)

life-atlas/
├── device-schemas/
│   ├── macbook-personal.md
│   ├── macbook-work.md
│   ├── pc.md
│   ├── nas-structure.md
│   ├── ipad.md
│   └── iphone.md
├── folder-schemas/
│   ├── workspace.md
│   ├── vault.md
│   ├── media.md
│   └── system.md
├── environment/
│   ├── mac-setup.md
│   ├── nas-setup.md
│   ├── shell-aliases.sh
│   └── devtools.sh
├── bookmarks/
│   ├── personal.md
│   ├── syntheus.md
│   ├── work.md
│   └── reading-list.md
├── .gitignore
└── README.md

## Streamlined Life Atlas Schema

### 🎯 Clean Structure Design

Based on your feedback, here's the streamlined approach that eliminates confusion:

#### Key Changes

- **Consolidate everything** under `~/Kit/` on MacBook
- **Remove LiveDocs** concept entirely
- **Move Photos** into Kit for regular sync
- **Perfect 1:1 mapping** between MacBook and NAS

### 📱 MacBook Pro (Personal) — Streamlined Structure

```
~/
├── Applications/             # App-specific config/data
├── Desktop/                  # Ephemeral, cleared weekly
├── Documents/                # Default macOS folder (mostly unused)
├── Downloads/                # Inbound items only, triaged regularly
├── Kit/                      # 🔨 Complete working environment (synced to NAS)
│   ├── Workspace/            # Active projects (personal, work, consulting, academic)
│   ├── Docs/                 # Important documents (taxes, legal, health, etc.)
│   ├── Photos/               # DSLR + drone content with regular updates
│   ├── Config/               # App configs, preferences, dotfiles
│   ├── System/               # Core scripts, automation, setup files
│   └── Temp/                 # Temporary working files
└── Vault/ → /Volumes/Vault/  # ❄️ NAS-mounted cold storage (read-only)
```

#### Migration Strategy

- **Move** `~/Workspace/` → `~/Kit/Workspace/`
- **Move** `~/Media/Photos/` → `~/Kit/Photos/`
- **Move** `~/System/` → `~/Kit/System/`
- **Delete** `~/LiveDocs/` (consolidate into `~/Kit/Docs/`)
- **Add** `~/Kit/Config/` for app-specific configurations
- **Add** `~/Kit/Temp/` for temporary working files

## 📦 UGREEN NAS — Streamlined Structure

```
/home/
├── Kit/                        # Perfect 1:1 mirror of MacBook's ~/Kit/
│   ├── Workspace/              # Active projects (bidirectional sync)
│   ├── Docs/                   # Important documents (bidirectional sync)
│   ├── Photos/                 # DSLR + drone content (bidirectional sync)
│   ├── Config/                 # App configs, preferences
│   ├── System/                 # Dotfiles, scripts
│   └── Temp/                   # Temporary files (maybe exclude from sync)
└── Vault/                      # Long-term cold storage (NAS-only)
    ├── DocsArchive/
    │   ├── Identity/
    │   ├── Health/
    │   ├── Finance/
    │   │   ├── Taxes/
    │   │   │   ├── 2024/
    │   │   │   ├── 2023/
    │   │   │   └── 2022/
    │   │   └── Statements/
    │   ├── Government/
    │   └── Legal/
    ├── WorkspaceArchive/
    │   ├── 2025/
    │   ├── 2024/
    │   └── Completed-Projects/
    ├── MediaArchive/
    │   ├── Photos/
    │   │   ├── 2025/
    │   │   ├── 2024/
    │   │   └── 2023/
    │   └── Videos/
    └── Snapshots/              # System snapshots, config backups

/volume1/
├── Media/                      # Plex + family media library
│   ├── books/
│   ├── downloads/
│   ├── movies/
│   ├── music/
│   ├── photos/                 # Family photos (different from personal archive)
│   └── tvshows/
├── docker/                     # Container persistent data
└── Time Machine A/             # macOS Time Machine backup
```

## 🔄 Streamlined Sync Strategy

| Location | Mac Path | NAS Path | Sync Method | Direction | Notes |
| --- | --- | --- | --- | --- | --- |
| **Complete Kit** | `~/Kit/` | `/home/Kit/` | Syncthing/rsync | ↔ Bidirectional | Everything in one sync |
| **Cold Archive** | `~/Vault/` (mounted) | `/home/Vault/` | NAS mount | ← Read-only | Browse/retrieve only |
| **System Backup** | `~/` (entire system) | `/volume1/Time Machine A/` | Time Machine | → Mac to NAS | Automatic |

### Sync Simplification Benefits

- **Single sync point**: Only `~/Kit/` needs active syncing
- **Photos included**: No separate media sync workflow needed  
- **Consistent structure**: Identical paths reduce confusion
- **Complete backup**: Kit contains everything actively used

## 🚀 Implementation Scripts

### MacBook Migration Script (`Kit/System/migrate-to-kit.sh`)

```bash
#!/bin/bash
# Life Atlas MacBook Migration to Kit Structure

echo "=== Migrating to streamlined Kit structure ==="

# Create new Kit structure
mkdir -p ~/Kit/{Workspace,Docs,Photos,Config,System,Temp}

# Migrate existing folders
if [ -d ~/Workspace ]; then
    echo "Moving ~/Workspace to ~/Kit/Workspace/"
    mv ~/Workspace/* ~/Kit/Workspace/ 2>/dev/null || true
    rmdir ~/Workspace 2>/dev/null || echo "Workspace had remaining files, please check manually"
fi

if [ -d ~/Media/Photos ]; then
    echo "Moving ~/Media/Photos to ~/Kit/Photos/"
    mv ~/Media/Photos/* ~/Kit/Photos/ 2>/dev/null || true
    rmdir ~/Media/Photos 2>/dev/null
    rmdir ~/Media 2>/dev/null || echo "Media folder has other content, keeping it"
fi

if [ -d ~/System ]; then
    echo "Moving ~/System to ~/Kit/System/"
    mv ~/System/* ~/Kit/System/ 2>/dev/null || true
    rmdir ~/System 2>/dev/null || echo "System had remaining files, please check manually"
fi

# Handle LiveDocs removal (migrate important content to Docs)
if [ -d ~/LiveDocs ]; then
    echo "LiveDocs found - please manually review and move important files to ~/Kit/Docs/"
    echo "Contents of LiveDocs:"
    ls -la ~/LiveDocs/
    echo "After review, you can remove ~/LiveDocs"
fi

# Setup NAS mount point for Vault
mkdir -p ~/Vault
echo ""
echo "=== Next Steps ==="
echo "1. Setup NAS mount: //nas-ip/home/Vault ~/Vault"
echo "2. Configure Syncthing to sync ~/Kit/ with NAS:/home/Kit/"
echo "3. Review ~/LiveDocs and migrate to ~/Kit/Docs/ then delete"
echo ""
echo "Migration complete! Your new structure:"
tree ~/Kit/ 2>/dev/null || ls -la ~/Kit/
```

### NAS Sync Script (`Kit/System/sync-kit.sh`)

```bash
#!/bin/bash
# Simplified Kit sync script

NAS_IP="your-nas-ip"
# Note: Using /home/Kit instead of /home/andrewhml/Kit

# Sync entire Kit (excluding Temp for performance)
rsync -avz --progress --exclude="Temp/" \
    ~/Kit/ root@${NAS_IP}:/home/Kit/

echo "Kit sync completed - all folders synchronized"
```

### Syncthing Configuration

```yaml
# Syncthing folder configuration
folder_id: "kit-sync"
label: "Life Atlas Kit"
path: 
  - local: "~/Kit"
  - remote: "/home/Kit"
ignored_patterns:
  - "Temp/*"
  - "*.tmp"
  - ".DS_Store"
  - "node_modules/"
  - ".git/"
versioning: "simple"
keep_versions: 10
```

## 📋 Streamlined Workflows

### Photo Management Workflow

1. **Import**: DSLR/drone content directly to `~/Kit/Photos/YYYY/`
2. **Process**: Edit in Lightroom/Photoshop (library stays in Kit)
3. **Sync**: Automatically synced to NAS via Kit sync
4. **Archive**: Move older/processed content to `Vault/MediaArchive/` when needed

### Document Lifecycle

1. **Active**: All documents in `~/Kit/Docs/`
2. **Organized**: Use subfolders (Identity/, Health/, Finance/, Legal/)
3. **Archive**: Move to `Vault/DocsArchive/` when no longer active
4. **Access**: Browse archived docs via mounted `~/Vault/`

### Project Lifecycle

1. **Active**: All projects in `~/Kit/Workspace/`
2. **Complete**: Archive to `Vault/WorkspaceArchive/YYYY/`
3. **Git repos**: Can stay in Workspace if still referenced

## 🔧 Tool Configurations

### Syncthing Configuration

- **Device ID**: Link MacBook with NAS
- **Folder**: `~/Kit/` ↔ `/home/andrewhml/Kit/`
- **Ignore Patterns**:
  - `Temp/*`
  - `*.tmp`
  - `.DS_Store`
  - `node_modules/`

### NAS Mount Script (macOS)

```bash
# Add to login items or crontab
mount_smbfs //andrewhml@nas-ip/andrewhml/Vault ~/Vault
```

### Backup Verification Script

```bash
#!/bin/bash
# Verify critical folders are synced

echo "=== Life Atlas Sync Status ==="
echo "Kit sync: $(rsync -an ~/Kit/ nas:/home/andrewhml/Kit/ | wc -l) differences"
echo "Vault mount: $(ls ~/Vault/ | wc -l) items accessible"
echo "Time Machine: $(tmutil latestbackup)"
```

## 🎯 Benefits of Streamlined Structure

1. **Perfect 1:1 Mapping**: `~/Kit/` exactly matches `/home/Kit/` - no confusion
2. **Single Sync Point**: Only one folder to keep in sync between devices
3. **Photos Included**: No separate media workflow - everything in Kit
4. **LiveDocs Eliminated**: Cleaner structure without redundant concepts
5. **Tool Integration**: All your VS Code, Raycast, AI tools work from one location
6. **Scalable**: Easy to add new categories within Kit structure
7. **Predictable**: Always know where files are and how they sync

## 🔄 Implementation Steps

1. **Run migration script** to restructure your MacBook
2. **Remove LiveDocs** after migrating important content to Kit/Docs
3. **Set up Kit sync** using Syncthing or rsync
4. **Configure Vault mount** for archive access
5. **Update tool configurations** to point to new Kit structure
6. **Test sync** to ensure everything works smoothly

This streamlined approach eliminates all the confusion while maintaining your workflow-focused design. Everything you actively work with lives in Kit and syncs automatically.
