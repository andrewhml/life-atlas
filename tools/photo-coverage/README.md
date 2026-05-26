# photo-coverage

Diagnostic and reconciliation tool for Immich photo libraries. Companion to Plan 0006 — `docs/plans/0006-photo-coverage-and-icloud-drain.md`.

The problem it solves: Immich libraries that grew through mixed import paths (iOS auto-backup, web UI upload of Google Takeout, manual rsync, external libraries) often contain assets with degraded bytes or wrong metadata. A sample-based spot check can pass while whole classes fail systematically. This tool measures the scope before committing to a fix strategy.

**Read-only. Writes nothing to Immich.**

## Status

Early. First-pass scope is the preflight diagnostic — `preflight.py`. Full coverage tool (Immich ↔ iCloud matching via `osxphotos`, four-bucket classification) arrives only if the preflight shows the work is justified.

## Requirements

- Python 3.9+ (no third-party dependencies)
- Immich instance reachable over HTTP
- Immich API key — generate from the web UI under Account Settings → API Keys. Read access is sufficient.

## Scripts

| Script | Purpose | Destructive? |
|---|---|---|
| `preflight.py` | Scans the whole Immich library and reports three bucket counts: small DNGs (byte-degradation proxy), upload-time-as-capture-date (Google Takeout signature), daily `fileCreatedAt` histogram (import clusters). | No |

## Setup

```sh
cd tools/photo-coverage
cp .env.example .env
# edit .env with your Immich server URL + API key
```

## Preflight — usage

```sh
python3 preflight.py > report.md
```

Scans every asset via paginated `/api/search/metadata` calls. A ~96k-asset library takes 1–5 minutes end-to-end. Outputs a markdown report to stdout (or `--output PATH`).

### What the three buckets mean

1. **DNGs under 2 MB** — Flags DNG assets stored at a small fraction of their expected original size. A clean iPhone ProRAW DNG is 8–40 MB. Anything below 2 MB is almost certainly a proxy (Google Photos stored a downgraded version, which Takeout then exported and Immich ingested as the "original").

2. **Upload-time-as-capture-date** — Flags assets whose `dateTimeOriginal` is within 5 seconds of their Immich `fileModifiedAt`. This is the fingerprint of "Immich had no real EXIF date to read, fell back to the upload time." The most common cause is Google Takeout where JSON sidecars (which hold Google Photos' "when taken" field) were not applied during import — for example, uploading the unzipped Takeout through Immich's web UI, which ignores sidecars. The fix is a re-import via [`immich-go`](https://github.com/simulot/immich-go) in Takeout mode.

3. **Daily `fileCreatedAt` histogram** — Shows single-day import spikes. A spike of N thousand assets on one day almost always means "a Takeout or bulk import was uploaded that day." Correlates 1:1 with Bucket 2 when the import lost metadata.

### Interpretation guide

- **Bucket 1 small (< 500):** fix targeted assets by hand; skip the full Phase D tool.
- **Bucket 2 large (> 5,000):** `immich-go` Takeout re-import is the repair path.
- **Bucket 3 flat, Buckets 1+2 small:** Phase A was closer to passing than the sample suggested; Phase B–D may be lighter.

## Design principles (shared with `tools/immich-dedup/`)

- Read-only by default
- Standard-library-only Python
- Outputs are plain-text reports a human can read (or pipe into another tool)
- Classifier-first: prove the scope of a problem before writing any destructive code

## License

MIT — same as `tools/immich-dedup/`.
