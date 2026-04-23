# immich-dedup

A read-only classifier for Immich's duplicate detection output. It takes the raw list of duplicate groups Immich surfaces, sorts them into handling-appropriate buckets, and prints a markdown report.

The problem it solves: Immich's duplicate finder does a good job identifying duplicates but gives you one flat list to review. For a library with tens of thousands of duplicate assets, that list is unreviewable one-at-a-time. This tool splits the list into buckets where the right action is obvious (bit-identical, HEIC+JPEG pairs, bursts) and a smaller pile that genuinely needs human attention.

**This tool writes nothing to Immich.** It's a reporting layer only — intended as the first step before any destructive action.

## Status

Early. Currently produces a markdown report; does not drive any Immich state change. The intent is to grow into a fuller triage tool (possibly with a lightweight web UI for the remaining edge cases), but the first pass is deliberately narrow.

## Requirements

- Python 3.9+ (no third-party dependencies — standard library only)
- An Immich instance you can reach over HTTP
- An Immich API key with permission to read duplicates (`duplicate.read`)

## Install

Clone / copy the directory. There's nothing to install.

```sh
cd tools/immich-dedup
cp .env.example .env
# edit .env with your Immich URL and API key
```

## Workflow

The three scripts are designed to be used in order:

1. **`classify.py`** — fast bucket breakdown. Read the report, decide which buckets look interesting.
2. **`gallery.py`** — visual review. Open the HTML, scroll through samples per bucket, build confidence in the classification before trusting it at scale.
3. **`apply.py`** — execution. Per-bucket, dry-run by default, writes to Immich's trash (soft-delete, 30-day recovery).

```sh
# 1. Report (markdown)
python3 classify.py > report.md

# 2. Visual review (open in browser)
python3 gallery.py
open gallery.html

# 3. Dry-run (no writes)
python3 apply.py --bucket heic_jpeg_pair

# 3. Actually apply (writes to Immich trash)
python3 apply.py --bucket heic_jpeg_pair --confirm
```

### Optional flags

```sh
# classify.py
python3 classify.py --out report.md          # write to file instead of stdout
python3 classify.py --raw groups.json        # also dump the raw API response

# gallery.py
python3 gallery.py --samples 50              # 50 random groups per bucket (default: 20)
python3 gallery.py --size preview            # larger thumbnails (slower to fetch)
python3 gallery.py --seed 123                # different random sample

# apply.py
python3 apply.py --tier high                 # all buckets in the high-confidence tier
python3 apply.py --bucket a,b,c              # comma-separated buckets also work
python3 apply.py --bucket burst --limit 10   # canary: process at most 10 groups
python3 apply.py --bucket foo --confirm      # execute
python3 apply.py --bucket foo --confirm --yes  # skip the interactive prompt
```

### Safety posture of `apply.py`

- Dry-run by default. `--confirm` is required to write.
- Interactive "continue?" prompt when `--confirm` is used in a TTY. Bypass with `--yes`.
- Soft-delete only. Items land in Immich's trash with 30-day recovery; there is no hard-delete path in this tool.
- Every resolved group appended to `apply.log.jsonl` with the bucket, keeper ids, trashed ids, batch number, and the API response status. Errors are logged without aborting the remaining batches.
- Groups with no `suggestedKeepAssetIds` are skipped — the tool refuses to guess.

## Output

A markdown report with:

- Totals: number of duplicate groups, total assets across them, estimated reclaim in GB if Immich's `suggestedKeepAssetIds` is respected.
- **Bucket breakdown table** — counts and reclaim-in-GB per bucket.
- **Samples** — the first 3 groups from each bucket, so the bucket labels are legible and spot-checkable.

## Buckets

Buckets are tagged with a confidence tier so the report can group safe-to-bulk-accept groups separately from the ones that need a human. Ordering matters in the classifier: more-specific rules fire first, and `dominant_keeper` is a confidence-based catch-all that scoops up groups where Immich's suggestion is clearly correct on size/pixel asymmetry alone.

| Bucket | Confidence | Meaning | Typical handling |
|---|---|---|---|
| `heic_jpeg_pair` | high | Same image stored as both HEIC and JPEG (Live Photo exports, share-sheet derivatives). | Keeper: HEIC original. Bulk-accept. |
| `rendition_set` | high | One source photo plus its iOS Photos resolution renditions (`_1_105_c`, `_4_5005_c`), possibly with a same-photo-different-name copy. Detected via shared canonical filename stem. | Keeper: full-resolution original. Bulk-accept. |
| `dominant_keeper` | high | Catch-all: suggested keeper is ≥2× the nearest competitor (size or pixels), or holds the majority of bytes in the group. | Bulk-accept. |
| `burst` | medium | Same device, captures within 5 seconds. | Immich's size-based pick is usually right; sample-review ~5%. |
| `screenshots` | medium | PNG with no camera EXIF, filename like `Screenshot_*` or `IMG_*.PNG`. | Low-stakes bulk-accept. |
| `live_photo_pair` | review | Still image paired with a motion video via `livePhotoVideoId`. | Usually not a true duplicate — consider stacking instead of deleting. |
| `edge_case` | review | None of the above — cross-format, mixed dimensions, mixed favorites, etc. | Human review, one-by-one. |

Classification is conservative: anything that doesn't match a confident rule falls into `edge_case`. Better to over-flag than under-flag.

## Configuration

```env
# .env
IMMICH_URL=http://your-immich-host:2283
IMMICH_API_KEY=your-api-key-here
```

Get an API key from Immich: **Account settings → API Keys → New API Key**. The only permission needed for this tool is `duplicate.read`.

The URL should be the base URL of your Immich instance — do *not* include `/api`. The tool appends that itself.

## Roadmap

- `classify.py` — report only (v0, current)
- `apply.py` — apply Immich's suggestions to the safe buckets via `POST /api/duplicates/resolve`, with a required `--confirm` flag and dry-run default
- Lightweight web UI for reviewing the `edge_case` bucket 10 groups at a time instead of one
- Additional signals that Immich's built-in detection misses (e.g., near-duplicates that survived Immich's thresholds)

The v0 report is enough to decide whether subsequent phases are worth building. If the `bit_identical` + `heic_jpeg_pair` + `screenshots` buckets together cover ≳80% of your groups, Immich's built-in "Duplicate all" with a spot-check is probably sufficient — no further tooling needed.

## License

MIT. See [LICENSE](LICENSE).

## Contributing / feedback

This is incubating inside a larger personal-automation repo and will likely extract to its own repository once it stabilizes. In the meantime, issues and suggestions are welcome wherever this ends up hosted.
