# 🖥️ PC Defaults

**Status:** pending. The personal PC is being added to the life-atlas system.

This file will document system defaults applied during PC setup — parallel to `macos_defaults.md` / `defaults_settings.sh` for macOS.

See your own `~/Atlas/docs/gear/inventory.yaml` (your PC's device record) for the target folder layout and tooling inventory. The public schema template at `device-schemas/inventory.template.yaml` shows the shape.

---

## TODO

- [ ] Decide OS (Windows vs Linux vs dual-boot) and document the decision rationale
- [ ] Inventory installed tools (winget on Windows, apt/pacman/brew on Linux)
- [ ] Capture registry tweaks (Windows) or dconf / gsettings tweaks (Linux)
- [ ] Document equivalents of macOS `defaults write` commands (dock, finder, keyboard, trackpad, etc.)
- [ ] Write a `pc_defaults.ps1` or `pc_defaults.sh` script mirroring `macos_defaults.sh`
