# 📦 UGREEN NAS — Device Schema

This document defines the folder structure and role of the UGREEN NAS in the `life-atlas` system.

---

## 🔧 NAS Paths Overview

```
/home/andrewhml/
├── Kit/                        # Mirror of MacBook's working environment
└── Vault/                      # Long-term cold storage (not on Mac)

/volume1/
├── Media/
│   ├── books/
│   ├── downloads/
│   ├── movies/
│   ├── music/
│   ├── photos/
│   └── tvshows/
├── docker/                     # Containers (e.g. Plex, Immich)
└── Time Machine A/             # Time Machine backup for MacBook
```

---

## 🎒 Kit (Live Working Files)

This folder is kept in sync with the MacBook's `~/Kit/` directory.

```
Kit/
├── Docs/
├── Workspace/
├── Config/
├── System/
└── Temp/
```

> Use rsync or Syncthing to maintain this mirror. Kit contains actively used and frequently updated files.

---

## 🧊 Vault (Archive Storage)

Used exclusively for archiving documents, photos, or projects that are no longer needed on the MacBook.

```
Vault/
├── DocsArchive/
│   ├── Taxes/
│   ├── Identity/
│   └── Legal/
├── WorkspaceArchive/
├── MediaArchive/
└── Snapshots/
```

> Vault is not mounted on the Mac. It is accessible via NAS-only. Archive from `Kit/` manually or via scheduled scripts.

---

## 🎞️ Media Library

All Plex-readable or long-form media lives here:

```
/volume1/Media/
├── books/
├── downloads/
├── movies/
├── music/
├── photos/
└── tvshows/
```

- **Photos**: Archived DSLR and drone footage from `Media/Photos/YYYY`
- **Music/Movies/TV**: Plex libraries
- **Books**: PDFs/eBooks

---

## 🔁 Sync Strategy Summary

| Folder             | Sync Direction      | Method          | Notes                     |
|--------------------|---------------------|------------------|----------------------------|
| `Kit/`             | Mac ↔ NAS           | rsync / Syncthing | Active work folder        |
| `Vault/`           | NAS only            | Manual add/move | Cold storage archive      |
| `Media/photos/`    | Mac → NAS           | Manual archive  | DSLR + drone content only |
| `Time Machine A/`  | Mac → NAS           | macOS native    | System-wide backup        |

---

## 🛠️ Docker Volume

```
/volume1/docker/
```

Used for container data, including:
- Plex
- Immich (photos)
- Nginx Proxy Manager
- Other apps managed via Portainer

---

## ✅ Permissions Strategy

- Shared folders under `/volume1/Media` should be group-readable by Plex
- Personal folders like `/home/andrewhml/` should be accessible only to the user account
- Use separate users or groups for automation scripts if needed

---

## 📝 Notes

- `Vault/` is your master archive; nothing ever syncs it *back* to the Mac
- DSLR content is archived manually from Mac → NAS
- Mac setup script should mount `Time Machine A` and sync `Kit/` on boot/login
