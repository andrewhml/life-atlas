#!/usr/bin/env python3
"""
immich-dedup gallery: visual spot-check companion to classify.py.

Fetches duplicate groups, classifies them with the same rules as classify.py,
samples N random groups per bucket, pulls a thumbnail for every asset in each
sampled group, and writes a single self-contained HTML file with the
thumbnails embedded as base64 data URLs.

The goal is visual trust-building before running any destructive action.
Open the HTML in a browser, scroll through each bucket's sample, verify that
the highlighted keeper is the one you'd pick by eye. If every bucket's
samples look right, you can proceed with confidence. If not, tune the rules
or exclude that bucket from bulk-accept.

Usage:
    python3 gallery.py                       # gallery.html, 20 samples/bucket
    python3 gallery.py --samples 50          # wider spot-check
    python3 gallery.py --out review.html     # alternate output path
    python3 gallery.py --size preview        # larger thumbnails (slower to fetch)

No third-party Python dependencies.
"""

from __future__ import annotations

import argparse
import base64
import html
import os
import random
import sys
import urllib.error
import urllib.request
from collections import defaultdict

# Reuse classification logic from classify.py.
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import classify  # noqa: E402


DEFAULT_SAMPLES_PER_BUCKET = 20
DEFAULT_THUMBNAIL_SIZE = "thumbnail"  # options: thumbnail | preview | fullsize


def fetch_thumbnail(base_url: str, api_key: str, asset_id: str,
                    size: str = DEFAULT_THUMBNAIL_SIZE) -> tuple[bytes, str] | None:
    """Return (bytes, content_type) for an asset thumbnail, or None on failure."""
    url = (
        f"{base_url.rstrip('/')}/api/assets/{asset_id}/thumbnail"
        f"?size={size}"
    )
    req = urllib.request.Request(url, headers={"x-api-key": api_key})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
            content_type = resp.headers.get("Content-Type", "image/jpeg")
            return data, content_type
    except (urllib.error.URLError, urllib.error.HTTPError) as e:
        print(f"  ! thumbnail fetch failed for {asset_id}: {e}", file=sys.stderr)
        return None


def data_uri(data: bytes, content_type: str) -> str:
    return f"data:{content_type};base64,{base64.b64encode(data).decode('ascii')}"


# -------- HTML rendering --------

CSS = """
:root {
  --bg: #0f1115;
  --panel: #161a21;
  --text: #e5e7eb;
  --muted: #8b95a7;
  --border: #272c36;
  --keep: #10b981;
  --keep-dim: #065f46;
  --loser: #6b7280;
  --tier-high: #10b981;
  --tier-medium: #f59e0b;
  --tier-review: #ef4444;
}
* { box-sizing: border-box; }
body {
  margin: 0; padding: 2rem;
  font: 14px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: var(--bg); color: var(--text);
}
h1 { margin: 0 0 1rem; font-size: 1.6rem; }
.summary {
  display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem;
  margin-bottom: 2rem;
}
.tier-card {
  padding: 1rem; background: var(--panel); border-radius: 8px;
  border-left: 4px solid var(--border);
}
.tier-card.high { border-left-color: var(--tier-high); }
.tier-card.medium { border-left-color: var(--tier-medium); }
.tier-card.review { border-left-color: var(--tier-review); }
.tier-card .label { color: var(--muted); font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
.tier-card .count { font-size: 1.8rem; font-weight: 600; margin-top: 0.25rem; }
.tier-card .reclaim { color: var(--muted); margin-top: 0.25rem; }
h2 {
  margin: 2.5rem 0 0.5rem; padding-bottom: 0.5rem;
  border-bottom: 1px solid var(--border); font-size: 1.2rem;
}
h2 .tier-pill {
  display: inline-block; margin-left: 0.75rem;
  padding: 0.15rem 0.5rem; border-radius: 10px;
  font-size: 0.75rem; font-weight: 500; text-transform: uppercase;
}
.tier-pill.high { background: var(--keep-dim); color: var(--tier-high); }
.tier-pill.medium { background: #78350f; color: var(--tier-medium); }
.tier-pill.review { background: #7f1d1d; color: var(--tier-review); }
.bucket-description {
  color: var(--muted); font-size: 0.9rem; margin: 0 0 1rem;
}
.group {
  background: var(--panel); border: 1px solid var(--border);
  border-radius: 6px; padding: 0.75rem 1rem; margin-bottom: 1rem;
}
.group-meta {
  color: var(--muted); font-size: 0.8rem; margin-bottom: 0.75rem;
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
}
.assets {
  display: flex; flex-wrap: wrap; gap: 0.75rem;
}
.asset {
  width: 220px; background: var(--bg); border: 2px solid var(--border);
  border-radius: 4px; overflow: hidden; position: relative;
}
.asset.keeper { border-color: var(--keep); }
.asset img {
  display: block; width: 100%; height: 180px;
  object-fit: cover; background: #000;
}
.asset .badge {
  position: absolute; top: 0.4rem; left: 0.4rem;
  padding: 0.15rem 0.5rem; border-radius: 3px;
  font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
  letter-spacing: 0.04em;
}
.asset.keeper .badge { background: var(--keep); color: #000; }
.asset:not(.keeper) .badge { background: var(--loser); color: #fff; opacity: 0.9; }
.asset .meta { padding: 0.4rem 0.5rem; font-size: 0.75rem; line-height: 1.35; }
.asset .filename {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.asset .dims { color: var(--muted); }
.empty { color: var(--muted); font-style: italic; padding: 0.5rem 0; }
"""


def _fmt_bytes_gb(n: int) -> str:
    return f"{n / 1024**3:.1f} GB"


def render_gallery_html(groups: list[dict], base_url: str, api_key: str,
                        samples_per_bucket: int, thumbnail_size: str,
                        seed: int) -> str:
    rng = random.Random(seed)

    # Classify once, bucket once.
    buckets: dict[str, list[dict]] = defaultdict(list)
    bucket_reclaim: dict[str, int] = defaultdict(int)
    for g in groups:
        b = classify.classify(g)
        buckets[b].append(g)
        bucket_reclaim[b] += classify.reclaim_bytes(g)

    def tier_totals(tier: str) -> tuple[int, int]:
        count = sum(
            len(buckets.get(b, []))
            for b, t in classify.BUCKET_CONFIDENCE.items()
            if t == tier
        )
        reclaim = sum(
            bucket_reclaim[b]
            for b, t in classify.BUCKET_CONFIDENCE.items()
            if t == tier
        )
        return count, reclaim

    lines: list[str] = []
    lines.append("<!DOCTYPE html>")
    lines.append('<html lang="en">')
    lines.append("<head>")
    lines.append('<meta charset="utf-8">')
    lines.append(f"<title>Immich Dedup Review — {html.escape(base_url)}</title>")
    lines.append(f"<style>{CSS}</style>")
    lines.append("</head>")
    lines.append("<body>")
    lines.append("<h1>Immich duplicate review gallery</h1>")
    lines.append(
        f"<p class='bucket-description'>"
        f"{len(groups):,} duplicate groups · "
        f"{samples_per_bucket} random samples per bucket · "
        f"{html.escape(base_url)}"
        f"</p>"
    )

    # Top-level tier summary cards.
    lines.append("<div class='summary'>")
    for tier, _label in classify.CONFIDENCE_TIERS:
        count, reclaim = tier_totals(tier)
        lines.append(
            f"<div class='tier-card {tier}'>"
            f"<div class='label'>{tier}</div>"
            f"<div class='count'>{count:,} groups</div>"
            f"<div class='reclaim'>{_fmt_bytes_gb(reclaim)} reclaim</div>"
            f"</div>"
        )
    lines.append("</div>")

    # Per-bucket sections, ordered by tier then bucket order.
    total_assets_to_fetch = 0
    plan: list[tuple[str, list[dict]]] = []
    for tier, _label in classify.CONFIDENCE_TIERS:
        for b in classify.BUCKETS:
            if classify.BUCKET_CONFIDENCE.get(b) != tier:
                continue
            pool = buckets.get(b, [])
            if not pool:
                continue
            k = min(samples_per_bucket, len(pool))
            sampled = rng.sample(pool, k)
            plan.append((b, sampled))
            total_assets_to_fetch += sum(
                len(g.get("assets") or []) for g in sampled
            )

    print(
        f"[gallery] fetching {total_assets_to_fetch} thumbnails "
        f"across {sum(len(s) for _, s in plan)} groups…",
        file=sys.stderr,
    )

    fetched = 0
    for b, sampled in plan:
        tier = classify.BUCKET_CONFIDENCE.get(b, "review")
        total_in_bucket = len(buckets.get(b, []))
        description = classify.BUCKET_DESCRIPTIONS.get(b, "")
        lines.append(
            f"<h2>{html.escape(b)} "
            f"<span class='tier-pill {tier}'>{tier}</span>"
            f"<span class='bucket-description' style='margin-left:0.75rem;font-weight:400;'>"
            f"{len(sampled)} samples of {total_in_bucket:,}"
            f"</span></h2>"
        )
        lines.append(f"<p class='bucket-description'>{html.escape(description)}</p>")

        for g in sampled:
            gid = html.escape(str(g.get("duplicateId", "?")))
            asset_count = len(g.get("assets") or [])
            lines.append("<div class='group'>")
            lines.append(
                f"<div class='group-meta'>group {gid} · {asset_count} assets</div>"
            )
            lines.append("<div class='assets'>")
            keep_ids = set(g.get("suggestedKeepAssetIds") or [])
            for a in g.get("assets") or []:
                fetched += 1
                if fetched % 50 == 0:
                    print(
                        f"[gallery] fetched {fetched}/{total_assets_to_fetch}",
                        file=sys.stderr,
                    )
                is_keeper = a.get("id") in keep_ids
                thumb = fetch_thumbnail(base_url, api_key, a["id"], thumbnail_size)
                img_src = (
                    data_uri(thumb[0], thumb[1])
                    if thumb else
                    "data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='220' height='180'><rect width='220' height='180' fill='%23222'/><text x='110' y='95' fill='%23888' font-family='sans-serif' font-size='13' text-anchor='middle'>no thumbnail</text></svg>"
                )
                exif = a.get("exifInfo") or {}
                size_mb = (exif.get("fileSizeInByte") or 0) / 1024**2
                dims = f"{a.get('width') or '?'}×{a.get('height') or '?'}"
                filename = html.escape(a.get("originalFileName") or "?")
                make_model = html.escape(
                    f"{exif.get('make') or ''} {exif.get('model') or ''}".strip()
                )
                badge = "Keep" if is_keeper else "Trash"
                klass = "asset keeper" if is_keeper else "asset"
                lines.append(f"<div class='{klass}'>")
                lines.append(f"<span class='badge'>{badge}</span>")
                lines.append(f"<img src='{img_src}' loading='lazy'>")
                lines.append("<div class='meta'>")
                lines.append(f"<div class='filename' title='{filename}'>{filename}</div>")
                lines.append(
                    f"<div class='dims'>{dims} · {size_mb:.1f} MB</div>"
                )
                if make_model:
                    lines.append(f"<div class='dims'>{make_model}</div>")
                lines.append("</div>")  # .meta
                lines.append("</div>")  # .asset
            lines.append("</div>")  # .assets
            lines.append("</div>")  # .group

    print(f"[gallery] done — fetched {fetched} thumbnails", file=sys.stderr)

    lines.append("</body>")
    lines.append("</html>")
    return "\n".join(lines) + "\n"


# -------- main --------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Visual review gallery for Immich duplicate classification.",
    )
    parser.add_argument(
        "--env", default=".env",
        help="Path to .env file (default: ./.env).",
    )
    parser.add_argument(
        "--out", default="gallery.html",
        help="Output HTML path (default: gallery.html).",
    )
    parser.add_argument(
        "--samples", type=int, default=DEFAULT_SAMPLES_PER_BUCKET,
        help=f"Random sample size per bucket (default: {DEFAULT_SAMPLES_PER_BUCKET}).",
    )
    parser.add_argument(
        "--size", default=DEFAULT_THUMBNAIL_SIZE,
        choices=["thumbnail", "preview", "fullsize"],
        help=f"Thumbnail size to request from Immich (default: {DEFAULT_THUMBNAIL_SIZE}).",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed for sample selection (default: 42, for reproducibility).",
    )
    args = parser.parse_args(argv)

    classify.load_env(args.env)
    base_url = os.environ.get("IMMICH_URL")
    api_key = os.environ.get("IMMICH_API_KEY")
    if not base_url or not api_key:
        print(
            "error: IMMICH_URL and IMMICH_API_KEY must be set",
            file=sys.stderr,
        )
        return 2

    groups = classify.fetch_duplicates(base_url, api_key)
    html_out = render_gallery_html(
        groups, base_url, api_key,
        samples_per_bucket=args.samples,
        thumbnail_size=args.size,
        seed=args.seed,
    )
    with open(args.out, "w") as f:
        f.write(html_out)
    print(f"[gallery] wrote {args.out}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main())
