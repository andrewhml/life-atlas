#!/usr/bin/env python3
"""
immich-dedup apply: execute bucket-filtered duplicate resolution.

Works in tandem with classify.py. Fetches the current duplicate list from
Immich, filters to the buckets you specify, and calls Immich's
/api/duplicates/resolve endpoint to move the non-keeper assets to the trash.

Safety posture:
    - Dry-run by default. No writes until you pass --confirm.
    - Interactive confirmation prompt when --confirm is used in a TTY.
    - Soft-delete only. Items land in Immich's trash with 30-day recovery.
    - Every action is appended to a JSONL log, one entry per group.
    - Errors in a batch are logged and the run continues; they don't abort
      the remaining batches, so partial failures don't leave the library
      in a half-processed state.

Usage:
    python3 apply.py --bucket heic_jpeg_pair              # dry-run, 8 groups
    python3 apply.py --bucket heic_jpeg_pair --confirm    # actually apply
    python3 apply.py --tier high --limit 10 --confirm     # canary: 10 groups
    python3 apply.py --tier high --confirm                # full run, high-tier only
    python3 apply.py --bucket rendition_set,dominant_keeper --confirm

No third-party Python dependencies.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import classify  # noqa: E402


DEFAULT_BATCH_SIZE = 50
DEFAULT_LOG_PATH = "apply.log.jsonl"
DEFAULT_HTTP_TIMEOUT = 300.0   # /duplicates/resolve does meaningful DB work
DEFAULT_RETRIES = 3            # for transient socket timeouts / connection resets


# Exceptions that indicate a transient network/server issue worth retrying
# (and then, if retries exhaust, worth logging-and-continuing rather than
# aborting the whole run). OSError is the important one here — socket.timeout
# inherits from it in Python 3.9+, and ConnectionError / BrokenPipeError
# also subclass it.
TRANSIENT_EXCEPTIONS = (
    urllib.error.URLError,
    urllib.error.HTTPError,
    OSError,
    json.JSONDecodeError,
)


# -------- group selection (pure, testable) --------

def select_groups(
    groups: list[dict],
    bucket_filter: set[str] | None = None,
    limit: int | None = None,
) -> list[tuple[str, dict]]:
    """Pick groups to resolve. Returns list of (bucket_label, resolve_dto).

    A group is selected iff:
      - its classified bucket is in `bucket_filter` (if provided), and
      - it has ≥1 suggested keeper asset id (we refuse to guess), and
      - there is ≥1 non-keeper asset to trash.

    The resolve_dto is shaped for the `/api/duplicates/resolve` endpoint:
        {duplicateId, keepAssetIds, trashAssetIds}
    """
    out: list[tuple[str, dict]] = []
    for g in groups:
        b = classify.classify(g)
        if bucket_filter is not None and b not in bucket_filter:
            continue
        keep_ids = list(g.get("suggestedKeepAssetIds") or [])
        if not keep_ids:
            continue
        keep_set = set(keep_ids)
        all_ids = [a.get("id") for a in (g.get("assets") or []) if a.get("id")]
        trash_ids = [aid for aid in all_ids if aid not in keep_set]
        if not trash_ids:
            continue
        out.append((b, {
            "duplicateId": g.get("duplicateId"),
            "keepAssetIds": keep_ids,
            "trashAssetIds": trash_ids,
        }))
        if limit is not None and len(out) >= limit:
            break
    return out


def expand_bucket_filter(
    bucket_args: list[str] | None,
    tier_arg: str | None,
) -> set[str]:
    """Merge --bucket and --tier arguments into a normalized set of bucket names."""
    result: set[str] = set()
    if bucket_args:
        for item in bucket_args:
            for name in item.split(","):
                name = name.strip()
                if name:
                    result.add(name)
    if tier_arg:
        for b, t in classify.BUCKET_CONFIDENCE.items():
            if t == tier_arg:
                result.add(b)
    return result


# -------- Immich API --------

def post_resolve_batch(base_url: str, api_key: str,
                       batch: list[dict],
                       timeout: float = DEFAULT_HTTP_TIMEOUT,
                       retries: int = DEFAULT_RETRIES) -> list[dict]:
    """POST /duplicates/resolve with retry on transient failures.

    Retries on any TRANSIENT_EXCEPTIONS with exponential backoff (1s, 2s, 4s).
    Re-raises the last error after the final attempt so the caller can log it.
    """
    body = json.dumps({"groups": batch}).encode()
    last_err: Exception | None = None
    for attempt in range(retries):
        req = urllib.request.Request(
            f"{base_url.rstrip('/')}/api/duplicates/resolve",
            data=body,
            headers={
                "x-api-key": api_key,
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except TRANSIENT_EXCEPTIONS as e:
            last_err = e
            if attempt < retries - 1:
                wait = 2 ** attempt  # 1s, 2s, 4s
                print(
                    f"    attempt {attempt + 1}/{retries} failed "
                    f"({type(e).__name__}: {e}); retrying in {wait}s…",
                    file=sys.stderr,
                )
                time.sleep(wait)
    # All retries exhausted — re-raise so the caller logs it and moves on.
    assert last_err is not None
    raise last_err


# -------- main --------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Apply Immich duplicate resolution per bucket. "
                    "Soft-delete only (items go to Immich trash, 30-day recovery).",
    )
    parser.add_argument("--env", default=".env",
                        help="Path to .env file (default: ./.env).")
    parser.add_argument(
        "--bucket", action="append", default=None,
        help="Bucket to include. Repeatable; comma-separated also accepted.",
    )
    parser.add_argument(
        "--tier", choices=["high", "medium", "review"], default=None,
        help="Include all buckets in a confidence tier.",
    )
    parser.add_argument(
        "--limit", type=int, default=None,
        help="Cap on groups to process (use for canary runs).",
    )
    parser.add_argument(
        "--confirm", action="store_true",
        help="Actually execute. Without this flag, this is a dry-run.",
    )
    parser.add_argument(
        "--yes", action="store_true",
        help="Skip the interactive prompt when --confirm is used in a TTY.",
    )
    parser.add_argument(
        "--log", default=DEFAULT_LOG_PATH,
        help=f"Append JSONL log of actions (default: {DEFAULT_LOG_PATH}).",
    )
    parser.add_argument(
        "--batch-size", type=int, default=DEFAULT_BATCH_SIZE,
        help=f"Groups per API call (default: {DEFAULT_BATCH_SIZE}).",
    )
    args = parser.parse_args(argv)

    # Bucket / tier filter.
    buckets = expand_bucket_filter(args.bucket, args.tier)
    if not buckets:
        print("error: must specify at least one --bucket or --tier",
              file=sys.stderr)
        return 2
    unknown = buckets - set(classify.BUCKETS)
    if unknown:
        print(f"error: unknown bucket(s): {', '.join(sorted(unknown))}",
              file=sys.stderr)
        print(f"valid buckets: {', '.join(classify.BUCKETS)}", file=sys.stderr)
        return 2

    # Env.
    classify.load_env(args.env)
    base_url = os.environ.get("IMMICH_URL")
    api_key = os.environ.get("IMMICH_API_KEY")
    if not base_url or not api_key:
        print("error: IMMICH_URL and IMMICH_API_KEY must be set",
              file=sys.stderr)
        return 2

    print("[apply] fetching duplicates…", file=sys.stderr)
    groups = classify.fetch_duplicates(base_url, api_key)

    selected = select_groups(groups, bucket_filter=buckets, limit=args.limit)
    total_groups = len(selected)
    total_trash = sum(len(dto["trashAssetIds"]) for _, dto in selected)

    mode = "APPLY" if args.confirm else "DRY-RUN"
    print(
        f"[{mode}] {total_groups} groups selected · {total_trash} assets to trash · "
        f"buckets: {', '.join(sorted(buckets))}"
        + (f" · limit {args.limit}" if args.limit else ""),
        file=sys.stderr,
    )

    # Dry-run preview.
    if not args.confirm:
        by_bucket = defaultdict(int)
        for b, _ in selected:
            by_bucket[b] += 1
        for b in classify.BUCKETS:
            if b in by_bucket:
                print(f"    {b:20s} {by_bucket[b]:,} groups", file=sys.stderr)
        if total_groups:
            preview = selected[: min(5, total_groups)]
            print("\n[dry-run] first 5 (of this run):", file=sys.stderr)
            for b, dto in preview:
                print(
                    f"    {b:20s} group {dto['duplicateId']} · "
                    f"keep {len(dto['keepAssetIds'])} · "
                    f"trash {len(dto['trashAssetIds'])}",
                    file=sys.stderr,
                )
        print("\n[dry-run] no changes made. Re-run with --confirm to write.",
              file=sys.stderr)
        return 0

    # Interactive confirmation (TTY only, skippable with --yes).
    if sys.stdin.isatty() and not args.yes:
        print(
            f"\n*** About to trash {total_trash} assets across "
            f"{total_groups} groups. ***\n"
            f"*** Soft-delete → Immich trash (30-day recovery). ***\n"
            f"*** Buckets: {', '.join(sorted(buckets))}. ***\n"
            f"*** Log: {args.log} ***\n"
            f"Continue? [y/N]: ",
            end="", file=sys.stderr, flush=True,
        )
        response = input().strip().lower()
        if response != "y":
            print("[abort] user cancelled", file=sys.stderr)
            return 1

    # Execute.
    log_file = open(args.log, "a")
    trashed = 0
    errored = 0
    try:
        for i in range(0, total_groups, args.batch_size):
            window = selected[i : i + args.batch_size]
            batch_num = i // args.batch_size + 1
            total_batches = (total_groups + args.batch_size - 1) // args.batch_size
            print(
                f"[APPLY] batch {batch_num}/{total_batches} "
                f"({len(window)} groups)…",
                file=sys.stderr,
            )
            payload = [dto for _, dto in window]
            ts = datetime.now(timezone.utc).isoformat(timespec="seconds")
            try:
                resp = post_resolve_batch(base_url, api_key, payload)
                for b, dto in window:
                    log_file.write(json.dumps({
                        "ts": ts,
                        "bucket": b,
                        "duplicateId": dto["duplicateId"],
                        "keepAssetIds": dto["keepAssetIds"],
                        "trashAssetIds": dto["trashAssetIds"],
                        "batch": batch_num,
                        "response_ok": True,
                    }) + "\n")
                    trashed += len(dto["trashAssetIds"])
                log_file.flush()
            except TRANSIENT_EXCEPTIONS as e:
                errored += sum(len(dto["trashAssetIds"]) for _, dto in window)
                log_file.write(json.dumps({
                    "ts": ts,
                    "batch": batch_num,
                    "error": f"{type(e).__name__}: {e}",
                    "group_ids": [dto["duplicateId"] for _, dto in window],
                }) + "\n")
                log_file.flush()
                print(
                    f"    ! batch {batch_num} failed after retries "
                    f"({type(e).__name__}: {e}); continuing",
                    file=sys.stderr,
                )
    finally:
        log_file.close()

    print(
        f"[APPLY] done · trashed {trashed} assets · "
        f"{errored} errors · log: {args.log}",
        file=sys.stderr,
    )
    return 0 if errored == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
