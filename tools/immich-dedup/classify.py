#!/usr/bin/env python3
"""
immich-dedup: classify Immich duplicate groups into actionable buckets.

Fetches duplicate groups from an Immich instance, categorizes them by the
kind of duplicate they are (bit-identical, HEIC/JPEG pair, burst, screenshot,
Live Photo pair, or edge case), and prints a markdown report. Writes nothing
back to Immich.

The goal is to turn "24,000 duplicates to review" into "18,000 duplicates of
a type that can be bulk-handled + 2,000 real edge cases worth human attention."

Usage:
    cp .env.example .env   # fill in IMMICH_URL and IMMICH_API_KEY
    python3 classify.py > report.md

No third-party Python dependencies. Standard library only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone


# Ordering matters: most-specific / highest-confidence buckets fire first.
BUCKETS = [
    "heic_jpeg_pair",
    "live_photo_pair",
    "rendition_set",
    "burst",
    "screenshots",
    "dominant_keeper",
    "edge_case",
]

# How much human oversight each bucket warrants. The report groups by tier.
#   high   → safe to bulk-accept Immich's suggestion
#   medium → bulk-accept with a 5% sample check
#   review → per-group human judgment
BUCKET_CONFIDENCE = {
    "heic_jpeg_pair": "high",
    "rendition_set": "high",
    "dominant_keeper": "high",
    "burst": "medium",
    "screenshots": "medium",
    "live_photo_pair": "review",
    "edge_case": "review",
}

CONFIDENCE_TIERS = [
    ("high", "High confidence — safe to bulk-accept Immich's suggestion"),
    ("medium", "Medium confidence — bulk-accept with a 5% sample check"),
    ("review", "Needs review"),
]

# Regexes used for canonical-stem matching in rendition_set detection.
# Matches iOS Photos rendition suffixes and macOS Finder copy suffixes.
#
# iOS Photos writes several rendition variants per asset, distinguished by a
# trailing letter code:
#   _c = compressed / reduced-size delivery rendition
#   _o = original-format rendition
#   _a = adjusted (edited) rendition
# All appear as `_<n>_<nnn>_[aco]` or `_<nnnn>_[aco]` at the end of the filename.
_EXT_RE = re.compile(r"\.[A-Za-z0-9]{2,5}$")
_RENDITION_SUFFIX_RE = re.compile(r"_\d+(_\d+)?_[aco]$")
_COPY_SUFFIX_RE = re.compile(r" \(\d+\)$")


# --- env loading ---

def load_env(path: str = ".env") -> None:
    if not os.path.isfile(path):
        return
    with open(path) as f:
        for raw in f:
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            os.environ.setdefault(
                key.strip(), val.strip().strip('"').strip("'")
            )


# --- Immich API ---

def fetch_duplicates(base_url: str, api_key: str) -> list[dict]:
    req = urllib.request.Request(
        f"{base_url.rstrip('/')}/api/duplicates",
        headers={"x-api-key": api_key, "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.load(resp)


# --- classification ---

def classify(group: dict) -> str:
    """Return the bucket label for a duplicate group.

    Ordering: most-specific rules fire first. Groups that don't match a
    specific pattern fall through to `dominant_keeper` (a confidence-based
    catch-all for when Immich's suggested keeper is clearly correct by size
    / pixel asymmetry), or finally `edge_case`.
    """
    assets = group.get("assets") or []
    if len(assets) < 2:
        return "edge_case"

    if is_heic_jpeg_pair(assets):
        return "heic_jpeg_pair"
    if is_live_photo_pair(assets):
        return "live_photo_pair"
    if is_rendition_set(assets):
        return "rendition_set"
    if is_burst(assets):
        return "burst"
    if is_screenshots(assets):
        return "screenshots"
    if is_dominant_keeper(group):
        return "dominant_keeper"
    return "edge_case"


def is_heic_jpeg_pair(assets: list[dict]) -> bool:
    mimes = [a.get("originalMimeType") or "" for a in assets]
    allowed = {"image/heic", "image/heif", "image/jpeg"}
    if not all(m in allowed for m in mimes):
        return False
    has_heic = any(m in ("image/heic", "image/heif") for m in mimes)
    has_jpeg = any(m == "image/jpeg" for m in mimes)
    return has_heic and has_jpeg


def is_live_photo_pair(assets: list[dict]) -> bool:
    # Live Photo = still image + short motion video paired via livePhotoVideoId.
    types = sorted(a.get("type") for a in assets)
    if types != ["IMAGE", "VIDEO"]:
        return False
    ids = {a.get("id") for a in assets}
    return any(a.get("livePhotoVideoId") in ids for a in assets)


def is_screenshots(assets: list[dict]) -> bool:
    return all(_is_screenshot_asset(a) for a in assets)


def _is_screenshot_asset(asset: dict) -> bool:
    exif = asset.get("exifInfo") or {}
    if exif.get("make"):
        return False
    name = (asset.get("originalFileName") or "").lower()
    mime = asset.get("originalMimeType") or ""
    if mime != "image/png":
        return False
    return name.startswith("screenshot") or name.startswith("img_")


def is_burst(assets: list[dict], span_seconds: float = 5.0) -> bool:
    # Same device + all captures within a short time window.
    devices = {
        ((a.get("exifInfo") or {}).get("make"),
         (a.get("exifInfo") or {}).get("model"))
        for a in assets
    }
    if len(devices) != 1:
        return False
    device = next(iter(devices))
    if device == (None, None):
        return False

    times = []
    for a in assets:
        ts = a.get("fileCreatedAt")
        if not ts:
            return False
        try:
            times.append(datetime.fromisoformat(ts.replace("Z", "+00:00")))
        except ValueError:
            return False
    span = (max(times) - min(times)).total_seconds()
    return span <= span_seconds


def canonical_stem(filename: str) -> str:
    """Strip extension + iOS rendition suffix + macOS copy suffix for comparison.

    Examples:
        "ADD78468-...710D.jpeg"              → "add78468-...710d"
        "ADD78468-...710D_1_105_c.jpeg"      → "add78468-...710d"
        "ADD78468-...710D_4_5005_c.jpeg"     → "add78468-...710d"
        "IMG_1014 (2).PNG"                   → "img_1014"
        "IMG_5371.PNG"                       → "img_5371"
    """
    stem = _EXT_RE.sub("", filename or "")
    stem = _RENDITION_SUFFIX_RE.sub("", stem)
    stem = _COPY_SUFFIX_RE.sub("", stem)
    return stem.lower()


def is_rendition_set(assets: list[dict]) -> bool:
    """True if ≥2 assets in the group share a canonical stem.

    Catches the common iOS Photos pattern: one original plus its
    auto-generated resolution renditions (_1_105_c, _4_5005_c, etc.),
    optionally mixed with a same-photo-different-name copy.
    """
    stems = [canonical_stem(a.get("originalFileName") or "") for a in assets]
    stems = [s for s in stems if s]
    if not stems:
        return False
    counts = Counter(stems)
    top_stem, top_count = counts.most_common(1)[0]
    return top_count >= 2


def is_dominant_keeper(group: dict) -> bool:
    """True when Immich's suggested keeper is clearly correct by size/pixel asymmetry.

    A confidence-based catch-all for groups that don't match a more specific
    pattern. Fires if *any* of:
      - keeper's file size ≥ sum of all losers' sizes (keeper holds majority of bytes)
      - keeper's pixel count ≥ 2× the largest loser's pixel count
      - keeper's file size ≥ 2× the largest loser's file size
    """
    keep_ids = set(group.get("suggestedKeepAssetIds") or [])
    assets = group.get("assets") or []
    if not keep_ids:
        return False
    keepers = [a for a in assets if a.get("id") in keep_ids]
    losers = [a for a in assets if a.get("id") not in keep_ids]
    if not keepers or not losers:
        return False

    keeper = keepers[0]
    keeper_size = asset_size(keeper)
    keeper_pixels = (keeper.get("width") or 0) * (keeper.get("height") or 0)

    loser_sizes = [asset_size(a) for a in losers]
    loser_pixels = [(a.get("width") or 0) * (a.get("height") or 0) for a in losers]
    max_loser_size = max(loser_sizes) if loser_sizes else 0
    max_loser_pixels = max(loser_pixels) if loser_pixels else 0
    total_loser_size = sum(loser_sizes)

    if keeper_size > 0 and keeper_size >= total_loser_size:
        return True
    if keeper_pixels > 0 and keeper_pixels >= 2 * max_loser_pixels:
        return True
    if max_loser_size > 0 and keeper_size >= 2 * max_loser_size:
        return True
    return False


# --- reclaim estimate ---

def asset_size(asset: dict) -> int:
    return (asset.get("exifInfo") or {}).get("fileSizeInByte") or 0


def reclaim_bytes(group: dict) -> int:
    """Bytes freed if Immich's `suggestedKeepAssetIds` is respected.

    Falls back to keeping the single largest asset when Immich has no
    suggestion for the group.
    """
    assets = group.get("assets") or []
    keep_ids = set(group.get("suggestedKeepAssetIds") or [])
    if keep_ids:
        losers = [a for a in assets if a.get("id") not in keep_ids]
    else:
        ordered = sorted(assets, key=asset_size, reverse=True)
        losers = ordered[1:]
    return sum(asset_size(a) for a in losers)


# --- reporting ---

BUCKET_DESCRIPTIONS = {
    "heic_jpeg_pair": "Same image stored as both HEIC and JPEG (Live Photo exports, share-sheet derivatives). Typical keeper: HEIC original.",
    "rendition_set": "One source photo plus its iOS Photos resolution renditions (`_1_105_c`, `_4_5005_c`, etc.). Immich's size-based suggestion picks the full-resolution original.",
    "dominant_keeper": "Immich's suggested keeper is overwhelmingly correct by size/pixel asymmetry (≥2× the nearest competitor, or majority of total bytes).",
    "burst": "Same device, captures within 5 seconds. Immich's size-based suggestion is usually right.",
    "screenshots": "PNG with no camera EXIF, filename like `Screenshot_*` or `IMG_*.PNG`. Low-stakes.",
    "live_photo_pair": "A still image paired with its short motion video via `livePhotoVideoId`. Usually not a true duplicate — may warrant stacking, not deleting.",
    "edge_case": "None of the above. Needs a human eye.",
}


def render_report(groups: list[dict], base_url: str) -> str:
    total_groups = len(groups)
    total_assets = sum(len(g.get("assets") or []) for g in groups)

    buckets: dict[str, list[dict]] = defaultdict(list)
    bucket_reclaim: dict[str, int] = defaultdict(int)
    total_reclaim = 0

    for g in groups:
        b = classify(g)
        buckets[b].append(g)
        r = reclaim_bytes(g)
        bucket_reclaim[b] += r
        total_reclaim += r

    def tier_totals(tier: str) -> tuple[int, int]:
        count = sum(
            len(buckets.get(b, []))
            for b, t in BUCKET_CONFIDENCE.items()
            if t == tier
        )
        reclaim = sum(
            bucket_reclaim[b]
            for b, t in BUCKET_CONFIDENCE.items()
            if t == tier
        )
        return count, reclaim

    now = datetime.now(timezone.utc).isoformat(timespec="seconds")
    lines: list[str] = []

    lines.append("# Immich duplicate classification report")
    lines.append("")
    lines.append(f"- Generated: {now}")
    lines.append(f"- Source: {base_url}")
    lines.append(f"- Total duplicate groups: {total_groups:,}")
    lines.append(f"- Total assets across groups: {total_assets:,}")
    lines.append(
        f"- Estimated reclaim if Immich's suggestions respected: "
        f"{total_reclaim / 1024**3:.1f} GB"
    )
    lines.append("")

    lines.append("## Actionable summary")
    lines.append("")
    for tier, _label in CONFIDENCE_TIERS:
        count, reclaim = tier_totals(tier)
        pct = (100 * count / total_groups) if total_groups else 0.0
        lines.append(
            f"- **{tier}**: {count:,} groups ({pct:.1f}%) · "
            f"{reclaim / 1024**3:.1f} GB reclaim"
        )
    lines.append("")

    lines.append("## Bucket breakdown by confidence tier")
    lines.append("")

    for tier, label in CONFIDENCE_TIERS:
        tier_buckets = [b for b in BUCKETS if BUCKET_CONFIDENCE.get(b) == tier]
        if not tier_buckets or all(not buckets.get(b) for b in tier_buckets):
            continue
        lines.append(f"### {label}")
        lines.append("")
        lines.append("| Bucket | Groups | % of groups | Reclaim (GB) |")
        lines.append("|---|---:|---:|---:|")
        for b in tier_buckets:
            count = len(buckets.get(b, []))
            pct = (100 * count / total_groups) if total_groups else 0.0
            gb = bucket_reclaim[b] / 1024**3
            lines.append(f"| {b} | {count:,} | {pct:.1f}% | {gb:.1f} |")
        lines.append("")

    lines.append("## What each bucket means")
    lines.append("")
    for b in BUCKETS:
        desc = BUCKET_DESCRIPTIONS.get(b, "")
        lines.append(f"- **{b}** — {desc}")
    lines.append("")

    lines.append("## Samples (first 3 groups per bucket)")
    for b in BUCKETS:
        samples = buckets.get(b, [])[:3]
        if not samples:
            continue
        lines.append("")
        lines.append(f"### {b}")
        lines.append("")
        for g in samples:
            lines.append(
                f"**group `{g.get('duplicateId', '?')}`** — "
                f"{len(g.get('assets') or [])} assets"
            )
            lines.append("")
            for a in g.get("assets") or []:
                exif = a.get("exifInfo") or {}
                size_mb = asset_size(a) / 1024**2
                make = exif.get("make") or ""
                model = exif.get("model") or ""
                dims = f"{a.get('width', '?')}×{a.get('height', '?')}"
                keep = (
                    " **(suggested keep)**"
                    if a.get("id") in (g.get("suggestedKeepAssetIds") or [])
                    else ""
                )
                device = f"{make} {model}".strip()
                device_part = f" · {device}" if device else ""
                lines.append(
                    f"- `{a.get('originalFileName', '?')}` · "
                    f"{a.get('originalMimeType', '?')} · "
                    f"{dims} · {size_mb:.1f} MB{device_part}{keep}"
                )
            lines.append("")

    return "\n".join(lines) + "\n"


# --- main ---

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Classify Immich duplicate groups for easier bulk triage.",
    )
    parser.add_argument(
        "--env",
        default=".env",
        help="Path to .env file (default: ./.env). Reads IMMICH_URL and IMMICH_API_KEY.",
    )
    parser.add_argument(
        "--out",
        default=None,
        help="Write the report to a file (default: stdout).",
    )
    parser.add_argument(
        "--raw",
        default=None,
        help="Also dump the raw /duplicates response to this path for offline inspection.",
    )
    args = parser.parse_args(argv)

    load_env(args.env)
    base_url = os.environ.get("IMMICH_URL")
    api_key = os.environ.get("IMMICH_API_KEY")
    if not base_url or not api_key:
        print(
            "error: IMMICH_URL and IMMICH_API_KEY must be set "
            "(copy .env.example to .env and fill them in)",
            file=sys.stderr,
        )
        return 2

    groups = fetch_duplicates(base_url, api_key)

    if args.raw:
        with open(args.raw, "w") as f:
            json.dump(groups, f, indent=2)

    report = render_report(groups, base_url)

    if args.out:
        with open(args.out, "w") as f:
            f.write(report)
    else:
        sys.stdout.write(report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
