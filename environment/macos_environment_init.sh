#!/bin/bash

# Atlas Structure Demo Script - Clean Version
# Creates non-destructive example folder structures

set -e

# Define variables
ATLAS_EXAMPLE="$HOME/Atlas-Example"
WORKSPACE_EXAMPLE="$HOME/Workspace-Example"
MEDIA_EXAMPLE="$HOME/Media-Example"
SYSTEM_EXAMPLE="$HOME/System-Example"
CURRENT_YEAR=$(date +%Y)

echo "=================================================="
echo "🗺️  Atlas Structure Demo - Example Folders"
echo "=================================================="
echo ""
echo "This script creates EXAMPLE folders that demonstrate the"
echo "Atlas structure. You can use these as templates."
echo ""
echo "No existing folders will be modified."
echo ""

read -p "Create example folder structures? (y/n): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Demo cancelled."
    exit 0
fi

echo "🏗️  Creating example structures..."
echo ""

# STEP 1: Create all top-level directories first
echo "📁 Creating top-level example directories..."
mkdir -p "$ATLAS_EXAMPLE"
mkdir -p "$WORKSPACE_EXAMPLE"
mkdir -p "$MEDIA_EXAMPLE"
mkdir -p "$SYSTEM_EXAMPLE"
echo "✅ Top-level directories created"
echo ""

# STEP 2: Create all subdirectory structures
echo "📁 Creating Atlas-Example/ structure..."
mkdir -p "$ATLAS_EXAMPLE/Docs"/{Identity,Health,Finance,Legal,Travel,Auto,Housing,Reference}
mkdir -p "$ATLAS_EXAMPLE/Config"/{Desktop-Images,Settings,Shortcuts,Templates}
mkdir -p "$ATLAS_EXAMPLE/Config/Shortcuts"/{iOS-Shortcuts,Raycast-Scripts,Cross-Platform}
mkdir -p "$ATLAS_EXAMPLE/Config/Templates"/{Documents,Code,Presentations,Forms}
mkdir -p "$ATLAS_EXAMPLE/Archive"

echo "📁 Creating Workspace-Example/ structure..."
mkdir -p "$WORKSPACE_EXAMPLE"/{Syntheus,Personal,Work,Academic,Environments}
mkdir -p "$WORKSPACE_EXAMPLE/Syntheus"/{Active-Projects,Proposals,Resources,Admin,Internal}
mkdir -p "$WORKSPACE_EXAMPLE/Work"/{Active-Projects,Development,Documentation,Archive}
mkdir -p "$WORKSPACE_EXAMPLE/Academic"/{High-School,College,Graduate-School,Continuing-Education}
mkdir -p "$WORKSPACE_EXAMPLE/Environments"/{Node-Projects,Python-Envs,Docker,Databases}

echo "📁 Creating Media-Example/ structure..."
mkdir -p "$MEDIA_EXAMPLE"/{Photos,Music}
mkdir -p "$MEDIA_EXAMPLE/Photos"/{Import,Lightroom-Library}
mkdir -p "$MEDIA_EXAMPLE/Photos/${CURRENT_YEAR}-Photos"/{RAW,Processed,Video}

# Create monthly RAW folders for current year
for month in 01 02 03 04 05 06 07 08 09 10 11 12; do
    mkdir -p "$MEDIA_EXAMPLE/Photos/${CURRENT_YEAR}-Photos/RAW/${CURRENT_YEAR}-${month}"
done

# Create YYYY-Photos template
mkdir -p "$MEDIA_EXAMPLE/Photos/YYYY-Photos"/{RAW,Processed,Video}
for month in 01 02 03 04 05 06 07 08 09 10 11 12; do
    mkdir -p "$MEDIA_EXAMPLE/Photos/YYYY-Photos/RAW/YYYY-${month}"
done

echo "📁 Creating System-Example/ structure..."
mkdir -p "$SYSTEM_EXAMPLE"/{Dotfiles,Scripts,Homebrew,Preferences,Setup,Backups}

echo "✅ All folder structures created successfully!"
echo ""

# STEP 3: Create all documentation files
echo "📝 Creating documentation files..."

# Atlas Example README
cat > "$ATLAS_EXAMPLE/README.md" << 'EOF'
# Atlas Example - Google Drive Integration Demo

This is an EXAMPLE of the Atlas structure designed for Google Drive integration.

## How to Use This Example

1. **Review the structure** - explore the folders to understand the organization
2. **Adapt to your setup** - copy/move folders that work for your existing Google Drive
3. **Customize as needed** - modify folder names and structure to fit your workflow
4. **Delete when done** - this is just a demo, feel free to remove it

## Structure Overview

This example demonstrates how Atlas can work as your Google Drive root folder:
- **Docs/**: Important documents accessible everywhere
- **Config/**: Cross-device configurations and scripts
- **Archive/**: Recently completed projects

## Google Drive Integration

If you choose to implement this structure:
- Make your actual Google Drive folder the "Atlas" equivalent
- Use UGREEN NAS Cloud Drives to sync with Google Drive
- Configure mobile apps for selective sync
- Keep local folders (Workspace, Media, System) separate from cloud sync

This is a template - adapt it to your needs!
EOF

# Config Example README
cat > "$ATLAS_EXAMPLE/Config/README.md" << 'EOF'
# Config Example - Cross-Device Settings

This folder shows how you might organize cross-device configurations.

## Example Organization

- **Desktop-Images/**: Wallpapers and backgrounds
- **Settings/**: App settings that work cross-platform
- **Shortcuts/**: Automation scripts and shortcuts
- **Templates/**: Reusable templates and boilerplates

## How to Adapt

1. Export browser bookmarks to bookmarks.html
2. Create Brewfile with: brew bundle dump
3. Add your own scripts and templates
4. Customize for your specific needs

Remember: This is just an example structure!
EOF

# Example Brewfile
cat > "$ATLAS_EXAMPLE/Config/Brewfile" << 'EOF'
# Atlas Brewfile Example - Package management for macOS setup
# This is an EXAMPLE file - adapt to your needs
# Generate your own with: brew bundle dump
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
# This is just an example - customize for your needs
EOF

# Workspace Example README
cat > "$WORKSPACE_EXAMPLE/README.md" << 'EOF'
# Workspace Example - Local Project Structure

This is an EXAMPLE of local project organization that stays on individual devices.

## Example Structure

- **Syntheus/**: Consulting company project organization
- **Personal/**: Personal projects (kept flat initially)
- **Work/**: Corporate work organization
- **Academic/**: Educational work by institution
- **Environments/**: Development environments with dependencies

## How to Use

1. Review the structure to understand the organization
2. Create similar folders in your actual workspace
3. Customize categories for your specific project types
4. Delete this example when done

Remember: This folder stays LOCAL (not synced to cloud)
EOF

# Media Example README
cat > "$MEDIA_EXAMPLE/README.md" << 'EOF'
# Media Example - Local Processing Structure

This is an EXAMPLE of local media file organization.

## Example Photo Workflow

1. **Import**: Camera/drone → Photos/Import/ (temporary)
2. **Organize**: Move to Photos/YYYY-Photos/RAW/YYYY-MM/
3. **Process**: Edit using Lightroom
4. **Export**: Final JPGs → Photos/YYYY-Photos/Processed/
5. **Archive**: Move completed years to long-term storage

## Example Structure

- **Import/**: Temporary triage folder
- **YYYY-Photos/**: Template - duplicate and rename for new years
- **2025-Photos/**: Current year example
- **Lightroom-Library/**: Lightroom catalogs

## How to Use

Duplicate the YYYY-Photos folder and rename it for each year.
Or use the create-photo-year.sh script for automation.

Remember: This folder stays LOCAL (not synced to cloud)
EOF

# System Example README
cat > "$SYSTEM_EXAMPLE/README.md" << 'EOF'
# System Example - Local Configuration Structure

This is an EXAMPLE of device-specific system configurations.

## Example Structure

- **Dotfiles/**: Shell and app configuration files
- **Scripts/**: Local automation and utility scripts
- **Homebrew/**: Package management configurations
- **Preferences/**: macOS app preferences
- **Setup/**: Device setup and installation scripts
- **Backups/**: Local configuration backups

## How to Use

1. Review the organization
2. Create similar structure for your actual system configs
3. Keep dotfiles in version control
4. Create setup scripts for new machine configuration

Remember: This folder stays LOCAL (not synced to cloud)
EOF

# YYYY-Photos template README
cat > "$MEDIA_EXAMPLE/Photos/YYYY-Photos/README.md" << 'EOF'
# YYYY-Photos Template Folder

This is a template folder for organizing photos by year.

## How to Use

### For Non-Technical Users
1. Right-click this "YYYY-Photos" folder
2. Select "Duplicate"
3. Rename the copy to your desired year (e.g., "2026-Photos")
4. Start organizing your photos in the new folder

### For Tech-Savvy Users
Use the create-photo-year.sh script in the Photos folder

## Folder Structure
- **RAW/**: Monthly folders (YYYY-01 through YYYY-12)
- **Processed/**: Final exported JPGs
- **Video/**: Video files for the year

## Organization Tips
Within monthly RAW folders, you can organize by:
- **Memories/**: Events, trips, occasions
- **Locations/**: Geographic organization
- Or keep files flat in the monthly folder
EOF

# Aliases suggestion file
cat > "$HOME/Atlas-Example-Aliases.txt" << 'EOF'
# Atlas Example Navigation Aliases
# These are EXAMPLE aliases - adapt paths for your actual setup
# Add modified versions to your ~/.zshrc file

# Quick navigation examples (modify paths as needed)
alias atlas="cd ~/Atlas"  # Change to your actual Google Drive folder
alias work="cd ~/Workspace"  # Change to your actual workspace
alias photos="cd ~/Media/Photos"  # Change to your actual media folder
alias config="cd ~/System"  # Change to your actual system configs

# Example project shortcuts
alias syntheus="cd ~/Workspace/Syntheus"  # Adapt to your structure
alias personal="cd ~/Workspace/Personal"  # Adapt to your structure

# Example utilities
alias show-structure="ls -la ~ | grep '^d'"

# Remember: These are examples - modify paths to match your actual setup!
EOF

echo "✅ Documentation files created!"
echo ""

# STEP 4: Create standalone scripts (AT THE END)
echo "📝 Creating standalone scripts..."

# Create the photo year creation script (SIMPLIFIED - terminal only)
cat > "$MEDIA_EXAMPLE/Photos/create-photo-year.sh" << 'EOF'
#!/bin/bash

# Create Photo Year Structure Script
# Creates organized photo folders for a specific year

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PHOTOS_DIR="$SCRIPT_DIR"

# Set default year to current year
CURRENT_YEAR=$(date +%Y)

echo "Create Photo Year Structure"
echo "=========================="
echo ""

# Get year from user or use command line argument
if [ $# -eq 1 ]; then
    # Year provided as command line argument
    YEAR="$1"
else
    # Get year from user input
    read -p "Enter year (default: $CURRENT_YEAR): " input
    YEAR="${input:-$CURRENT_YEAR}"
fi

echo "Using year: $YEAR"
echo ""

# Validate year format (4 digits)
if ! [[ "$YEAR" =~ ^[0-9]+$ ]] || [ ${#YEAR} -ne 4 ]; then
    echo "Error: Year must be exactly 4 digits (e.g., 2025). You entered: '$YEAR'"
    exit 1
fi

# Check if year is reasonable (between 1900 and 2100)
if [ "$YEAR" -lt 1900 ] || [ "$YEAR" -gt 2100 ]; then
    echo "Error: Year must be between 1900 and 2100. You entered: $YEAR"
    exit 1
fi

YEAR_FOLDER="$PHOTOS_DIR/${YEAR}-Photos"

# Check if year folder already exists
if [ -d "$YEAR_FOLDER" ]; then
    read -p "Folder ${YEAR}-Photos already exists! Continue and add missing subfolders? (y/n): " -n 1 -r
    echo ""
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Operation cancelled."
        exit 0
    fi
fi

echo "Creating photo structure for year $YEAR..."
echo ""

# Create year folder structure
mkdir -p "$YEAR_FOLDER"/{RAW,Processed,Video}

# Create monthly RAW folders
echo "Creating monthly folders..."
for month in 01 02 03 04 05 06 07 08 09 10 11 12; do
    MONTH_FOLDER="$YEAR_FOLDER/RAW/${YEAR}-${month}"
    mkdir -p "$MONTH_FOLDER"
    
    # Create example organization folders in first month only
    if [ "$month" == "01" ]; then
        mkdir -p "$MONTH_FOLDER/Memories"
        mkdir -p "$MONTH_FOLDER/Locations"
        
        # Create README for organization options
        cat > "$MONTH_FOLDER/README.md" << EOL
# ${YEAR}-${month} Photos

Raw photo files for $(date -j -f "%Y-%m" "${YEAR}-${month}" "+%B %Y" 2>/dev/null || echo "Month $month, $YEAR").

## Organization Options

You can organize photos in this folder by:

### By Memories/Events
Use the Memories/ subfolder or create folders like:
- Vacation-Trip/
- Birthday-Party/
- Weekend-Hiking/

### By Locations
Use the Locations/ subfolder or create folders like:
- Boston-Area/
- New-York-Trip/
- Home/

### Or keep flat
Just place all RAW files directly in this month folder.

## Workflow
1. Import RAW files here from camera/drone
2. Process in Lightroom (catalog in ../../../Lightroom-Library/)
3. Export processed JPGs to ../${YEAR}-Photos/Processed/
EOL
    fi
done

# Create main year folder README
cat > "$YEAR_FOLDER/README.md" << EOL
# ${YEAR} Photos

Photo organization for the year ${YEAR}.

## Folder Structure

### RAW/
Monthly folders (${YEAR}-01 through ${YEAR}-12) containing:
- Raw camera files organized by month
- Optional Memories/ and Locations/ subfolders for organization

### Processed/
Final exported JPG images from Lightroom/editing

### Video/
Video files captured during ${YEAR}

## Workflow
1. **Import**: Camera/drone content → RAW/YYYY-MM/
2. **Process**: Edit in Lightroom (catalog in ../Lightroom-Library/)
3. **Export**: Processed JPGs → Processed/
4. **Archive**: Move to long-term storage when year complete

Created: $(date)
EOL

echo "✅ Photo structure created successfully!"
echo ""
echo "📂 Created folders:"
echo "   $YEAR_FOLDER/RAW/ (with monthly subfolders ${YEAR}-01 through ${YEAR}-12)"
echo "   $YEAR_FOLDER/Processed/"
echo "   $YEAR_FOLDER/Video/"
echo ""
echo "📋 Next steps:"
echo "1. Import photos to appropriate monthly RAW folders"
echo "2. Use Lightroom catalog in ../Lightroom-Library/"
echo "3. Export processed images to $YEAR_FOLDER/Processed/"
echo "4. Organize by Memories or Locations as needed"
echo ""
EOF

chmod +x "$MEDIA_EXAMPLE/Photos/create-photo-year.sh"

echo "✅ Scripts created!"
echo ""

# Final summary
echo "=================================================="
echo "🎉 Atlas Example Structures Created!"
echo "=================================================="
echo ""
echo "📂 Example structures created:"
echo "   ~/Atlas-Example/        - Google Drive structure example"
echo "   ~/Workspace-Example/    - Local project structure example"
echo "   ~/Media-Example/        - Local media structure example"
echo "   ~/System-Example/       - Local system config structure example"
echo ""
echo "📋 How to use these examples:"
echo "1. Review each example structure to understand the organization"
echo "2. Copy/adapt folders that work for your existing setup"
echo "3. Install Google Drive Desktop App for your actual Atlas folder"
echo "4. Set up UGREEN NAS Cloud Drives to sync with Google Drive"
echo "5. Configure mobile Google Drive apps with selective sync"
echo "6. Check example aliases: cat ~/Atlas-Example-Aliases.txt"
echo "7. Test photo script: ~/Media-Example/Photos/create-photo-year.sh"
echo "8. Delete example folders when you're done with them"
echo ""
echo "📖 Read README files in each example folder for detailed guidance"
echo ""
echo "🗺️  These are examples to adapt - not a rigid system to follow!"