# macOS Defaults

**Status:** pending. Documents the preferred `defaults write` settings applied by `defaults_settings.sh`.

---

## TODO

Document, with rationale, each applied default:

- [ ] Dock behavior (autohide, size, orientation, recent apps)
- [ ] Finder (hidden files, path bar, status bar, default view, search scope)
- [ ] Keyboard (key repeat, initial repeat, full keyboard access)
- [ ] Trackpad (tap to click, three-finger drag, gestures)
- [ ] Screenshots (location, format, shadow, timestamp)
- [ ] Global appearance (dark mode, accent color, menu bar)
- [ ] Safari / browser defaults if relevant
- [ ] Terminal / Warp / iTerm defaults if relevant

Each entry should capture:
- The `defaults write` command
- What it does in plain English
- Why it's preferred
- How to revert (`defaults delete` or the inverse)
