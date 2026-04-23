"""Tests for apply.py group selection logic (no network)."""

from __future__ import annotations

import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
if PARENT not in sys.path:
    sys.path.insert(0, PARENT)

import apply  # noqa: E402
import classify  # noqa: E402


def _asset(**overrides):
    base = {
        "id": "asset-id",
        "checksum": "abc",
        "originalFileName": "IMG_0001.HEIC",
        "originalMimeType": "image/heic",
        "type": "IMAGE",
        "width": 4032,
        "height": 3024,
        "fileCreatedAt": "2025-06-01T12:00:00.000Z",
        "livePhotoVideoId": None,
        "exifInfo": {
            "make": "Apple", "model": "iPhone 16 Pro",
            "fileSizeInByte": 4_000_000,
        },
    }
    base.update(overrides)
    return base


def _heic_jpeg_group(gid="g1", keep="a"):
    return {
        "duplicateId": gid,
        "assets": [
            _asset(id="a", originalFileName="photo.heic",
                   originalMimeType="image/heic"),
            _asset(id="b", originalFileName="photo.jpg",
                   originalMimeType="image/jpeg"),
        ],
        "suggestedKeepAssetIds": [keep],
    }


def _rendition_group(gid="g2"):
    uuid = "add78468-93e5-442a-b241-2c412e48710d"
    return {
        "duplicateId": gid,
        "assets": [
            _asset(id="r1", originalFileName=f"{uuid}.jpeg",
                   originalMimeType="image/jpeg"),
            _asset(id="r2", originalFileName=f"{uuid}_1_105_c.jpeg",
                   originalMimeType="image/jpeg"),
            _asset(id="r3", originalFileName=f"{uuid}_4_5005_c.jpeg",
                   originalMimeType="image/jpeg"),
        ],
        "suggestedKeepAssetIds": ["r1"],
    }


class ExpandBucketFilterTests(unittest.TestCase):
    def test_single_bucket(self):
        self.assertEqual(
            apply.expand_bucket_filter(["rendition_set"], None),
            {"rendition_set"},
        )

    def test_comma_separated(self):
        self.assertEqual(
            apply.expand_bucket_filter(["rendition_set,heic_jpeg_pair"], None),
            {"rendition_set", "heic_jpeg_pair"},
        )

    def test_repeated_flag(self):
        self.assertEqual(
            apply.expand_bucket_filter(["burst", "screenshots"], None),
            {"burst", "screenshots"},
        )

    def test_tier_expands_to_all_buckets_in_tier(self):
        result = apply.expand_bucket_filter(None, "high")
        # The high tier currently includes: heic_jpeg_pair, rendition_set,
        # dominant_keeper. Assert the full set matches BUCKET_CONFIDENCE.
        expected = {
            b for b, t in classify.BUCKET_CONFIDENCE.items() if t == "high"
        }
        self.assertEqual(result, expected)

    def test_bucket_and_tier_union(self):
        result = apply.expand_bucket_filter(["burst"], "high")
        expected = {b for b, t in classify.BUCKET_CONFIDENCE.items() if t == "high"}
        expected.add("burst")
        self.assertEqual(result, expected)

    def test_empty(self):
        self.assertEqual(apply.expand_bucket_filter(None, None), set())


class SelectGroupsTests(unittest.TestCase):
    def test_filter_to_specific_bucket(self):
        groups = [_heic_jpeg_group("g1"), _rendition_group("g2")]
        selected = apply.select_groups(groups, bucket_filter={"heic_jpeg_pair"})
        self.assertEqual(len(selected), 1)
        self.assertEqual(selected[0][0], "heic_jpeg_pair")
        self.assertEqual(selected[0][1]["duplicateId"], "g1")

    def test_multiple_buckets_union(self):
        groups = [_heic_jpeg_group("g1"), _rendition_group("g2")]
        selected = apply.select_groups(
            groups, bucket_filter={"heic_jpeg_pair", "rendition_set"}
        )
        self.assertEqual(len(selected), 2)

    def test_limit_caps_output(self):
        groups = [_rendition_group(f"g{i}") for i in range(10)]
        selected = apply.select_groups(
            groups, bucket_filter={"rendition_set"}, limit=3,
        )
        self.assertEqual(len(selected), 3)

    def test_skips_groups_without_suggested_keeper(self):
        g = _rendition_group("g1")
        g["suggestedKeepAssetIds"] = []  # no suggestion
        selected = apply.select_groups([g], bucket_filter={"rendition_set"})
        self.assertEqual(selected, [])

    def test_trash_ids_exclude_keeper(self):
        g = _rendition_group("g1")
        selected = apply.select_groups([g], bucket_filter={"rendition_set"})
        self.assertEqual(len(selected), 1)
        _, dto = selected[0]
        self.assertEqual(dto["keepAssetIds"], ["r1"])
        self.assertEqual(sorted(dto["trashAssetIds"]), ["r2", "r3"])

    def test_resolve_dto_shape(self):
        g = _heic_jpeg_group("g1", keep="a")
        [(bucket, dto)] = apply.select_groups(
            [g], bucket_filter={"heic_jpeg_pair"}
        )
        self.assertEqual(bucket, "heic_jpeg_pair")
        self.assertEqual(set(dto.keys()),
                         {"duplicateId", "keepAssetIds", "trashAssetIds"})
        self.assertEqual(dto["duplicateId"], "g1")

    def test_skips_when_all_assets_are_keepers(self):
        # If suggested keepers covers every asset, there's nothing to trash.
        g = _heic_jpeg_group("g1", keep="a")
        g["suggestedKeepAssetIds"] = ["a", "b"]
        selected = apply.select_groups([g], bucket_filter={"heic_jpeg_pair"})
        self.assertEqual(selected, [])

    def test_no_bucket_filter_selects_all_classifiable(self):
        groups = [_heic_jpeg_group("g1"), _rendition_group("g2")]
        selected = apply.select_groups(groups, bucket_filter=None)
        self.assertEqual(len(selected), 2)


if __name__ == "__main__":
    unittest.main()
