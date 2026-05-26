#!/usr/bin/env python3
"""
photo-coverage preflight — diagnose Immich library degradation scope.

Read-only. Scans the Immich library via REST API and reports:
  1. DNG assets under a size threshold (likely proxies; RAW stripped to JPEG in DNG wrapper)
  2. Assets whose `dateTimeOriginal` equals (or is very close to) the server upload time
     — a strong signal that the asset has no real EXIF date and Immich fell back
     to upload time. This is the Google Takeout failure mode when JSON sidecars
     are ignored.
  3. Daily histogram of `fileCreatedAt` — spots import clusters.

Output: a markdown report to stdout (or --output PATH).

Usage:
    cp .env.example .env    # fill in IMMICH_SERVER_URL + IMMICH_API_KEY
    python3 preflight.py > report.md

No third-party dependencies. Python 3.9+.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterator
from urllib import error as urlerror
from urllib import parse as urlparse
from urllib import request as urlrequest

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

DNG_SIZE_THRESHOLD_MB = 2.0       # DNGs smaller than this are flagged as proxy candidates
UPLOAD_TIME_DELTA_SECONDS = 5     # dateTimeOriginal within N sec of upload = upload-time fallback
PAGE_SIZE = 1000
REQUEST_TIMEOUT_S = 60


# ---------------------------------------------------------------------------
# Env loader (minimal, avoids python-dotenv dependency)
# ---------------------------------------------------------------------------

def load_env(path: Path) -> None:
    if not path.exists():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            continue
        k, v = line.split("=", 1)
        k, v = k.strip(), v.strip().strip('"').strip("'")
        os.environ.setdefault(k, v)


# ---------------------------------------------------------------------------
# Immich client
# ---------------------------------------------------------------------------

class ImmichClient:
    def __init__(self, base_url: str, api_key: str) -> None:
        self.base = base_url.rstrip("/")
        self.api_key = api_key

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        url = self.base + path
        if params:
            url += "?" + urlparse.urlencode(params)
        req = urlrequest.Request(
            url,
            headers={"x-api-key": self.api_key, "Accept": "application/json"},
        )
        try:
            with urlrequest.urlopen(req, timeout=REQUEST_TIMEOUT_S) as resp:
                return json.loads(resp.read())
        except urlerror.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:400]
            raise RuntimeError(f"GET {path} -> HTTP {e.code}: {body}") from e

    def _post(self, path: str, body: dict[str, Any]) -> Any:
        data = json.dumps(body).encode("utf-8")
        req = urlrequest.Request(
            self.base + path,
            data=data,
            headers={
                "x-api-key": self.api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlrequest.urlopen(req, timeout=REQUEST_TIMEOUT_S) as resp:
                return json.loads(resp.read())
        except urlerror.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:400]
            raise RuntimeError(f"POST {path} -> HTTP {e.code}: {body}") from e

    def iter_assets(self) -> Iterator[dict[str, Any]]:
        """
        Stream every visible asset via /api/search/metadata, which paginates via `page`.
        This endpoint returns full asset records including `exifInfo`.
        """
        page = 1
        while True:
            resp = self._post(
                "/api/search/metadata",
                {"page": page, "size": PAGE_SIZE, "withExif": True},
            )
            assets_block = resp.get("assets", resp)
            items = assets_block.get("items", [])
            if not items:
                return
            for a in items:
                yield a
            next_page = assets_block.get("nextPage")
            if not next_page:
                return
            page = int(next_page)


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

@dataclass
class AssetSummary:
    id: str
    original_file_name: str
    file_size: int | None
    date_time_original: datetime | None
    file_created_at: datetime | None
    file_modified_at: datetime | None
    type_: str


@dataclass
class Findings:
    total: int = 0
    by_type: Counter = field(default_factory=Counter)
    dng_small: list[AssetSummary] = field(default_factory=list)
    dng_total: int = 0
    dng_total_size_bytes: int = 0
    upload_time_dates: list[AssetSummary] = field(default_factory=list)
    date_histogram: Counter = field(default_factory=Counter)
    missing_exif_date: int = 0


def parse_dt(val: str | None) -> datetime | None:
    if not val:
        return None
    try:
        # Immich returns ISO 8601 with Z or offset
        return datetime.fromisoformat(val.replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None


def summarize(asset: dict[str, Any]) -> AssetSummary:
    exif = asset.get("exifInfo") or {}
    file_size = exif.get("fileSizeInByte")
    if isinstance(file_size, str):
        try:
            file_size = int(file_size)
        except ValueError:
            file_size = None
    return AssetSummary(
        id=asset.get("id", ""),
        original_file_name=asset.get("originalFileName") or "",
        file_size=file_size,
        date_time_original=parse_dt(exif.get("dateTimeOriginal")),
        file_created_at=parse_dt(asset.get("fileCreatedAt")),
        file_modified_at=parse_dt(asset.get("fileModifiedAt")),
        type_=asset.get("type") or "",
    )


def analyze(client: ImmichClient, progress: bool = True) -> Findings:
    f = Findings()
    dng_threshold_bytes = int(DNG_SIZE_THRESHOLD_MB * 1024 * 1024)
    delta = timedelta(seconds=UPLOAD_TIME_DELTA_SECONDS)
    for i, raw in enumerate(client.iter_assets(), start=1):
        s = summarize(raw)
        f.total += 1
        f.by_type[s.type_] += 1

        lower = s.original_file_name.lower()
        if lower.endswith(".dng"):
            f.dng_total += 1
            if s.file_size is not None:
                f.dng_total_size_bytes += s.file_size
                if s.file_size < dng_threshold_bytes:
                    f.dng_small.append(s)

        if s.date_time_original is None:
            f.missing_exif_date += 1
        elif s.file_modified_at is not None:
            if abs(s.date_time_original - s.file_modified_at) <= delta:
                f.upload_time_dates.append(s)

        if s.file_created_at is not None:
            f.date_histogram[s.file_created_at.date().isoformat()] += 1

        if progress and i % 2000 == 0:
            print(f"  ... {i} assets scanned", file=sys.stderr, flush=True)

    return f


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def human_size(n: int | None) -> str:
    if n is None:
        return "?"
    units = ["B", "KB", "MB", "GB", "TB"]
    x = float(n)
    for u in units:
        if x < 1024 or u == units[-1]:
            return f"{x:,.1f} {u}"
        x /= 1024
    return f"{n} B"


def render_report(f: Findings) -> str:
    out: list[str] = []
    out.append("# photo-coverage preflight report")
    out.append("")
    out.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    out.append(f"Total assets scanned: **{f.total:,}**")
    out.append("")

    out.append("## Asset types")
    out.append("")
    out.append("| Type | Count |")
    out.append("|---|---:|")
    for t, n in f.by_type.most_common():
        out.append(f"| `{t or '(none)'}` | {n:,} |")
    out.append("")

    out.append("## Bucket 1 — DNGs under threshold (likely proxies)")
    out.append("")
    dng_small_pct = (len(f.dng_small) / f.dng_total * 100) if f.dng_total else 0.0
    out.append(f"- Threshold: `< {DNG_SIZE_THRESHOLD_MB} MB`")
    out.append(f"- Total DNGs: **{f.dng_total:,}**")
    out.append(f"- DNGs under threshold: **{len(f.dng_small):,}** ({dng_small_pct:.1f}%)")
    if f.dng_total:
        avg = f.dng_total_size_bytes / f.dng_total
        out.append(f"- Average DNG size: {human_size(int(avg))}")
    out.append("")
    if f.dng_small:
        out.append("First 20 candidate filenames (sorted by size, smallest first):")
        out.append("")
        sample = sorted(f.dng_small, key=lambda s: s.file_size or 0)[:20]
        out.append("| File | Size | Asset ID |")
        out.append("|---|---:|---|")
        for s in sample:
            out.append(f"| `{s.original_file_name}` | {human_size(s.file_size)} | `{s.id[:12]}…` |")
    out.append("")

    out.append("## Bucket 2 — Upload-time-as-capture-date (likely Takeout sidecars ignored)")
    out.append("")
    ut_pct = (len(f.upload_time_dates) / f.total * 100) if f.total else 0.0
    out.append(f"- Criterion: `|dateTimeOriginal - fileModifiedAt| ≤ {UPLOAD_TIME_DELTA_SECONDS}s`")
    out.append(f"- Assets flagged: **{len(f.upload_time_dates):,}** ({ut_pct:.1f}%)")
    out.append(f"- Assets with NO `dateTimeOriginal` at all: **{f.missing_exif_date:,}**")
    out.append("")
    if f.upload_time_dates:
        out.append("First 20 flagged (sorted by upload time):")
        out.append("")
        sample = sorted(
            f.upload_time_dates,
            key=lambda s: s.file_modified_at or datetime.min.replace(tzinfo=timezone.utc),
        )[:20]
        out.append("| File | dateTimeOriginal | fileModifiedAt | Asset ID |")
        out.append("|---|---|---|---|")
        for s in sample:
            dto = s.date_time_original.isoformat() if s.date_time_original else "(null)"
            fma = s.file_modified_at.isoformat() if s.file_modified_at else "(null)"
            out.append(f"| `{s.original_file_name}` | {dto} | {fma} | `{s.id[:12]}…` |")
    out.append("")

    out.append("## Bucket 3 — fileCreatedAt daily histogram (import clusters)")
    out.append("")
    out.append("Top 20 days by asset count. Spikes = single-day imports (e.g., Takeout runs).")
    out.append("")
    out.append("| Day | Count |")
    out.append("|---|---:|")
    for day, n in f.date_histogram.most_common(20):
        out.append(f"| `{day}` | {n:,} |")
    out.append("")

    out.append("## Interpretation guide")
    out.append("")
    out.append(
        "- **Bucket 1 population** scopes the byte-degradation problem. "
        "If large, iPhone/iCloud re-import is required for those DNGs. "
        "If small (< ~500), targeted per-asset re-import is easier than building the full Phase D tool."
    )
    out.append(
        "- **Bucket 2 population** scopes the metadata-degradation problem. "
        "Large → re-import via `immich-go` with Google Takeout mode (which reads JSON sidecars). "
        "Small → Phase D can patch individually."
    )
    out.append(
        "- **Bucket 3 spikes** identify import events. A single-day spike of N thousand "
        "correlates 1:1 with Bucket 2 if that import lost metadata. This confirms the cause."
    )
    return "\n".join(out) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    here = Path(__file__).resolve().parent
    load_env(here / ".env")

    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--output", "-o", type=Path, help="Write report to PATH instead of stdout.")
    parser.add_argument(
        "--server",
        default=os.environ.get("IMMICH_SERVER_URL"),
        help="Immich base URL (or $IMMICH_SERVER_URL).",
    )
    parser.add_argument(
        "--key",
        default=os.environ.get("IMMICH_API_KEY"),
        help="Immich API key (or $IMMICH_API_KEY).",
    )
    parser.add_argument(
        "--quiet", action="store_true", help="Suppress progress lines on stderr."
    )
    args = parser.parse_args()

    if not args.server or not args.key:
        print(
            "ERROR: Missing IMMICH_SERVER_URL or IMMICH_API_KEY. Set env vars or create .env.",
            file=sys.stderr,
        )
        return 2

    client = ImmichClient(args.server, args.key)

    print(f"Scanning {args.server} ...", file=sys.stderr, flush=True)
    findings = analyze(client, progress=not args.quiet)
    report = render_report(findings)

    if args.output:
        args.output.write_text(report)
        print(f"Report written to {args.output}", file=sys.stderr)
    else:
        sys.stdout.write(report)

    return 0


if __name__ == "__main__":
    sys.exit(main())
