#!/bin/bash

# Refined Atlas Structure Setup Script
# Creates the complete home directory structure with Atlas global sync

set -e  # Exit on any error

HOME_DIR="$HOME"
ATLAS_DIR="$HOME/Atlas"
BACKUP_DIR="$HOME/Atlas-Structure-Backup-$(date +%Y%m%d-%H%M%S)"
CURRENT_YEAR=$(date +%Y)

echo "=================================================="
echo "🗺️  Refined Atlas Structure Setup"
echo "=================================================="
echo ""

# Check if Atlas already exists and offer backup
if [ -d "$ATLAS_DIR" ]; then
    echo "⚠️  Atlas folder already exists at $ATLAS_DIR"
    echo "Creating backup at $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    cp -r "$ATLAS_DIR" "$BACKUP_DIR/Atlas-backup"
    echo "✅ Atlas backup created"
    echo ""
fi

# Check for existing Workspace and Media folders
EXISTING_FOLDERS=()
[ -d "$HOME/Workspace" ] && EXISTING_FOLDERS+=("Workspace")
[ -d "$HOME/Media" ] && EXISTING_FOLDERS+=("Media")
[ -d "$HOME/System" ] && EXISTING_FOLDERS+=("System")

if [ ${#EXISTING_FOLDERS[@]} -gt 0 ]; then
    echo "⚠️  Found existing folders: ${EXISTING_FOLDERS[*]}"
    echo "These will be backed up to $BACKUP_DIR"
    mkdir -p "$BACKUP_DIR"
    for folder in "${EXISTING_FOLDERS[@]}"; do
        if [ -d "$HOME/$folder" ]; then
            cp -r "$HOME/$folder" "$BACKUP_DIR/$folder-backup"
            echo "✅ Backed up $folder"
        fi
    done
    echo ""
    read -p "Continue with setup? This will create new folder structures. (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Setup cancelled."
        exit 0
    fi
fi

echo "🏗️  Creating Atlas structure..."
echo ""

# Create Atlas structure (Global sync content)
echo "📁 Creating ~/Atlas/ (Global sync content)..."
mkdir -p "$ATLAS_DIR"

# Atlas/Docs structure
mkdir -p "$ATLAS_DIR/Docs"/{Identity,Health,Finance,Legal,Travel,Auto,Housing,Reference}

# Atlas/Config structure
mkdir -p "$ATLAS_DIR/Config"/{Desktop-Images,Settings,Shortcuts,Templates}
mkdir -p "$ATLAS_DIR/Config/Shortcuts"/{iOS-Shortcuts,Raycast-Scripts,Cross-Platform}
mkdir -p "$ATLAS_DIR/Config/Templates"/{Documents,Code,Presentations,Forms}

# Atlas/Archive
mkdir -p "$ATLAS_DIR/Archive"

echo "📁 Creating ~/Workspace/ (Local projects)..."
# Workspace structure
mkdir -p "$HOME/Workspace"/{Syntheus,Personal,Work,Academic,Environments}

# Syntheus subfolders
mkdir -p "$HOME/Workspace/Syntheus"/{Active-Projects,Proposals,Resources,Admin,Internal}

# Work subfolders
mkdir -p "$HOME/Workspace/Work"/{Active-Projects,Development,Documentation,Archive}

# Academic subfolders
mkdir -p "$HOME/Workspace/Academic"/{High-School,College,Graduate-School,Continuing-Education}

# Environments subfolders
mkdir -p "$HOME/Workspace/Environments"/{Node-Projects,Python-Envs,Docker,Databases}

echo "📁 Creating ~/Media/ (Local media processing)..."
# Media structure
mkdir -p "$HOME/Media"/{Photos,Music}

# Photos structure with current year
mkdir -p "$HOME/Media/Photos"/{Import,Lightroom-Library}
mkdir -p "$HOME/Media/Photos/${CURRENT_YEAR}-Photos"/{RAW,Processed,Video}

# Create monthly RAW folders for current year
for month in {01..12}; do
    mkdir -p "$HOME/Media/Photos/${CURRENT_YEAR}-Photos/RAW/${CURRENT_YEAR}-${month}"
done

# Add previous year structure as example
PREV_YEAR=$((CURRENT_YEAR - 1))
mkdir -p "$HOME/Media/Photos/${PREV_YEAR}-Photos"/{RAW,Processed,Video}

echo "📁 Creating ~/System/ (Local system configs)..."
# System structure
mkdir -p "$HOME/System"/{Dotfiles,Scripts,Homebrew,Preferences,Setup,Backups}

echo "✅ Folder structure created successfully!"
echo ""

# Create helpful files
echo "📝 Creating helpful files and examples..."

# Create main README
cat > "$ATLAS_DIR/README.md" << EOF
# Atlas - Your Global Digital Hub

## Structure Overview

- **~/Atlas/**: Global content synced across all devices
- **~/Workspace/**: Local project work (not synced)
- **~/Media/**: Local media processing (not synced)
- **~/System/**: Local system configurations (not synced)

## Atlas Contents (Global Sync)

### Documents
- Important docs accessible from all devices
- Auto, Housing folders for vehicle and property records

### Config
- Cross-device configurations
- Single bookmarks.html file (export from browser)
- Brewfile for package management
- Desktop images and wallpapers

## Quick Navigation Tips

\`\`\`bash
# Add these aliases to ~/.zshrc
alias atlas="cd ~/Atlas"
alias work="cd ~/Workspace"
alias photos="cd ~/Media/Photos"
alias config="cd ~/System"
\`\`\`

Generated on $(date)
EOF

# Create Atlas Config examples
cat > "$ATLAS_DIR/Config/README.md" << EOF
# Atlas Config

Cross-device configuration files and settings.

## Files in this directory

- **bookmarks.html**: Export from your browser (Chrome: Bookmarks > Export bookmarks)
- **Brewfile**: Run \`brew bundle dump\` to create, \`brew bundle\` to install
- **Desktop-Images/**: Wallpapers and backgrounds synced across devices

## Shortcuts
- **iOS-Shortcuts/**: Export shortcuts from iPhone/iPad
- **Raycast-Scripts/**: Custom Raycast extensions and commands
- **Cross-Platform/**: Scripts that work on multiple operating systems

## Templates
- **Documents/**: Word, Pages, Markdown templates
- **Code/**: Project scaffolding and code snippets
- **Presentations/**: Slide deck templates
- **Forms/**: Common forms and checklists
EOF

# Create example Brewfile
cat > "$ATLAS_DIR/Config/Brewfile" << 'EOF'
# Atlas Brewfile - Package management for macOS setup
# Generate with: brew bundle dump
# Install with: brew bundle

# Taps
tap "homebrew/bundle"
tap "homebrew/cask"

# Core development tools
brew "git"
brew "node"
brew "python@3.11"
brew "zsh"

# Productivity tools
cask "raycast"
cask "visual-studio-code"
cask "obsidian"

# Media tools
cask "adobe-creative-cloud"

# Add your own packages here
EOF

# Create Workspace README
cat > "$HOME/Workspace/README.md" << EOF
# Workspace - Local Project Hub

All active project work, regardless of context.

## Structure

### Syntheus/
Consulting company projects and business operations

### Personal/
Personal projects (flat structure - add subfolders as needed)

### Work/
Corporate work projects (primarily on work MacBook)

### Academic/
Educational work organized by institution:
- High-School/
- College/
- Graduate-School/
- Continuing-Education/

### Environments/
Development environments with heavy dependencies

## Guidelines
- Keep active projects here while working on them
- Archive completed projects to Atlas/Archive/ or Vault
- Use git for version control where appropriate
EOF

# Create Media README
cat > "$HOME/Media/README.md" << EOF
# Media - Local Processing Hub

Large media files for device-specific processing.

## Photo Workflow

1. **Import**: DSLR/drone → Photos/Import/ (temporary triage)
2. **Organize**: Move to Photos/YYYY-Photos/RAW/YYYY-MM/
3. **Process**: Edit using Lightroom (catalog in Lightroom-Library/)
4. **Export**: Final JPGs → Photos/YYYY-Photos/Processed/
5. **Archive**: Move completed years to Vault

## Folder Structure

### Photos/
- **Import/**: Temporary folder - keep empty after processing
- **YYYY-Photos/**: Organized by year
  - **RAW/YYYY-MM/**: Monthly raw files (optionally organize by Memories/ or Locations/)
  - **Processed/**: Final exported images
  - **Video/**: Video files for the year
- **Lightroom-Library/**: Lightroom catalogs and previews

### Music/
Default macOS folder (mostly unused)
EOF

# Create System README
cat > "$HOME/System/README.md" << EOF
# System - Local Configuration Hub

Device-specific system configurations and automation.

## Structure

### Dotfiles/
Shell and application configuration files:
- .zshrc, .bash_profile
- .gitconfig, .vimrc
- Application-specific configs

### Scripts/
Local automation and utility scripts

### Homebrew/
Package management configurations and lists

### Preferences/
macOS application preferences and settings

### Setup/
Device setup and installation scripts

### Backups/
Local configuration backups and snapshots

## Usage
- Keep dotfiles in version control
- Create setup scripts for new machine configuration
- Regular backups of important configurations
EOF

# Create suggested aliases file
cat > "$HOME/Atlas-suggested-aliases.txt" << 'EOF'
# Atlas Navigation Aliases
# Add these to your ~/.zshrc file

# Quick navigation
alias atlas="cd ~/Atlas"
alias work="cd ~/Workspace"
alias photos="cd ~/Media/Photos"
alias config="cd ~/System"

# Project shortcuts
alias syntheus="cd ~/Workspace/Syntheus"
alias personal="cd ~/Workspace/Personal"

# Specific functions
alias photo-import="cd ~/Media/Photos/Import"
alias this-year="cd ~/Media/Photos/$(date +%Y)-Photos"

# Atlas utilities
alias atlas-tree="tree ~ -d -L 2 -I 'Library|Applications|Desktop|Documents|Downloads|Movies|Pictures|Public'"
alias show-structure="ls -la ~ | grep '^d'"

# Photo organization helpers
alias organize-photos="echo 'Move photos from ~/Media/Photos/Import/ to ~/Media/Photos/$(date +%Y)-Photos/RAW/$(date +%Y-%m)/'"
alias new-month="mkdir -p ~/Media/Photos/$(date +%Y)-Photos/RAW/$(date +%Y-%m)"
EOF

# Create desktop shortcuts if Desktop exists
if [ -d "$HOME/Desktop" ]; then
    echo "🔗 Creating desktop shortcuts..."
    ln -sf "$ATLAS_DIR" "$HOME/Desktop/Atlas"
    ln -sf "$HOME/Workspace/Syntheus" "$HOME/Desktop/Syntheus"
    ln -sf "$HOME/Workspace/Personal" "$HOME/Desktop/Personal"
    ln -sf "$HOME/Media/Photos" "$HOME/Desktop/Photos"
fi

# Create example monthly photo folders with README
cat > "$HOME/Media/Photos/${CURRENT_YEAR}-Photos/RAW/${CURRENT_YEAR}-$(date +%m)/README.md" << EOF
# $(date +%B) $(date +%Y) Photos

Raw photo files for $(date +%B) $(date +%Y).

## Organization Options

You can organize photos in this folder by:

### By Memories/Events
Create subfolders like:
- Vacation-Trip/
- Birthday-Party/
- Weekend-Hiking/

### By Locations
Create subfolders like:
- Boston-Area/
- New-York-Trip/
- Home/

### Or keep flat
Just place all RAW files directly in this folder.

## Workflow
1. Import RAW files here from camera/drone
2. Process in Lightroom (catalog in ~/Media/Photos/Lightroom-Library/)
3. Export processed JPGs to ~/Media/Photos/$(date +%Y)-Photos/Processed/
EOF

echo "✅ Helper files and examples created!"
echo ""

# Final setup instructions
echo "=================================================="
echo "🎉 Refined Atlas Setup Complete!"
echo "=================================================="
echo ""
echo "📂 Structure created:"
echo "   ~/Atlas/           - Global sync content"
echo "   ~/Workspace/       - Local project work"
echo "   ~/Media/           - Local media processing"
echo "   ~/System/          - Local system configs"
echo ""
echo "🔗 Desktop shortcuts created:"
echo "   Atlas → ~/Atlas/"
echo "   Syntheus → ~/Workspace/Syntheus/"
echo "   Personal → ~/Workspace/Personal/"
echo "   Photos → ~/Media/Photos/"
echo ""
echo "📋 Next steps:"
echo "1. Review structure: ls -la ~/"
echo "2. Add suggested aliases: cat ~/Atlas-suggested-aliases.txt"
echo "3. Set up browser bookmark export to ~/Atlas/Config/bookmarks.html"
echo "4. Create Brewfile: cd ~/Atlas/Config && brew bundle dump"
echo "5. Configure sync for ~/Atlas/ folder only"
echo "6. Test photo workflow with current month folder"
echo "7. Move existing projects into appropriate Workspace folders"
echo ""
echo "📖 Read individual README files in each folder for detailed guidance"
echo ""
echo "🗺️  Happy organizing with your new Atlas structure!"