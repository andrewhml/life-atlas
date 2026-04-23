"""Unit tests for the classification functions.

These tests exercise pure logic — no network, no Immich. Run with:

    python3 -m unittest discover -s tests -v

from within the tool directory.
"""

from __future__ import annotations

import os
import sys
import unittest

# Make classify.py importable when running from this directory or the repo root.
HERE = os.path.dirname(os.path.abspath(__file__))
PARENT = os.path.dirname(HERE)
if PARENT not in sys.path:
    sys.path.insert(0, PARENT)

import classify  # noqa: E402


def _asset(**overrides):
    """Build a minimal AssetResponseDto-shaped dict with overrides."""
    base = {
        "id": "00000000-0000-4000-8000-000000000000",
        "checksum": "abc",
        "originalFileName": "IMG_0001.HEIC",
        "originalMimeType": "image/heic",
        "type": "IMAGE",
        "width": 4032,
        "height": 3024,
        "fileCreatedAt": "2025-06-01T12:00:00.000Z",
        "livePhotoVideoId": None,
        "exifInfo": {
            "make": "Apple",
            "model": "iPhone 16 Pro",
            "fileSizeInByte": 4_000_000,
        },
    }
    base.update(overrides)
    return base


def _group(assets, suggested=None, duplicate_id="group-1"):
    return {
        "duplicateId": duplicate_id,
        "assets": assets,
        "suggestedKeepAssetIds": suggested or [],
    }


class CanonicalStemTests(unittest.TestCase):
    def test_strips_extension(self):
        self.assertEqual(classify.canonical_stem("IMG_1234.HEIC"), "img_1234")

    def test_strips_ios_rendition_suffix_four_number(self):
        self.assertEqual(
            classify.canonical_stem(
                "ADD78468-93E5-442A-B241-2C412E48710D_1_105_c.jpeg"
            ),
            "add78468-93e5-442a-b241-2c412e48710d",
        )

    def test_strips_ios_rendition_suffix_five_number(self):
        self.assertEqual(
            classify.canonical_stem(
                "ADD78468-93E5-442A-B241-2C412E48710D_4_5005_c.jpeg"
            ),
            "add78468-93e5-442a-b241-2c412e48710d",
        )

    def test_strips_ios_rendition_suffix_original_variant(self):
        # _o = original-format rendition
        self.assertEqual(
            classify.canonical_stem(
                "C1B35D14-ADBF-4348-8BEE-ACA696072B5B_1_102_o.jpeg"
            ),
            "c1b35d14-adbf-4348-8bee-aca696072b5b",
        )

    def test_strips_ios_rendition_suffix_adjusted_variant(self):
        # _a = adjusted (edited) rendition
        self.assertEqual(
            classify.canonical_stem(
                "EA8BE79F-2DA7-4200-B7A2-A37E9DE6EDA6_1_201_a.jpeg"
            ),
            "ea8be79f-2da7-4200-b7a2-a37e9de6eda6",
        )

    def test_strips_macos_copy_suffix(self):
        self.assertEqual(classify.canonical_stem("IMG_1014 (2).PNG"), "img_1014")


class ClassifyTests(unittest.TestCase):
    def test_heic_jpeg_pair(self):
        g = _group([
            _asset(id="a", originalFileName="photo1.heic",
                   originalMimeType="image/heic"),
            _asset(id="b", originalFileName="photo2.jpg",
                   originalMimeType="image/jpeg"),
        ])
        self.assertEqual(classify.classify(g), "heic_jpeg_pair")

    def test_live_photo_pair(self):
        g = _group([
            _asset(id="img", originalFileName="a.heic",
                   type="IMAGE", livePhotoVideoId="vid"),
            _asset(id="vid", originalFileName="a.mov", type="VIDEO",
                   originalMimeType="video/quicktime"),
        ])
        self.assertEqual(classify.classify(g), "live_photo_pair")

    def test_rendition_set_shared_uuid_stem(self):
        uuid = "add78468-93e5-442a-b241-2c412e48710d"
        g = _group([
            _asset(id="a", originalFileName=f"{uuid}.jpeg",
                   originalMimeType="image/jpeg"),
            _asset(id="b", originalFileName=f"{uuid}_1_105_c.jpeg",
                   originalMimeType="image/jpeg"),
            _asset(id="c", originalFileName=f"{uuid}_4_5005_c.jpeg",
                   originalMimeType="image/jpeg"),
        ])
        self.assertEqual(classify.classify(g), "rendition_set")

    def test_rendition_set_partial_match_with_outlier(self):
        uuid = "9cb5d371-a2be-4753-b9d9-6cb0ce2a2ac2"
        g = _group([
            _asset(id="a", originalFileName=f"{uuid}.jpeg",
                   originalMimeType="image/jpeg"),
            _asset(id="b", originalFileName="IMG_20181024_085750.jpg",
                   originalMimeType="image/jpeg"),
            _asset(id="c", originalFileName=f"{uuid}_1_105_c.jpeg",
                   originalMimeType="image/jpeg"),
        ])
        self.assertEqual(classify.classify(g), "rendition_set")

    def test_rendition_set_macos_copy_suffix(self):
        g = _group([
            _asset(id="a", originalFileName="IMG_1014.PNG",
                   originalMimeType="image/png",
                   exifInfo={"fileSizeInByte": 100_000}),
            _asset(id="b", originalFileName="IMG_1014 (2).PNG",
                   originalMimeType="image/png",
                   exifInfo={"fileSizeInByte": 200_000}),
        ])
        self.assertEqual(classify.classify(g), "rendition_set")

    def test_all_different_filenames_not_rendition_set(self):
        # Sequential screenshots or unrelated photos with distinct names
        # must NOT be classified as rendition_set.
        g = _group([
            _asset(id="a", originalFileName="IMG_5371.PNG",
                   originalMimeType="image/png", exifInfo={"fileSizeInByte": 100_000}),
            _asset(id="b", originalFileName="IMG_5372.PNG",
                   originalMimeType="image/png", exifInfo={"fileSizeInByte": 100_000}),
        ])
        # Falls through to screenshots bucket.
        self.assertEqual(classify.classify(g), "screenshots")

    def test_screenshots(self):
        g = _group([
            _asset(
                id="a", originalFileName="Screenshot_2025-06-01.png",
                originalMimeType="image/png",
                exifInfo={"fileSizeInByte": 1_000_000},
            ),
            _asset(
                id="b", originalFileName="screenshot_2025-06-02.png",
                originalMimeType="image/png",
                exifInfo={"fileSizeInByte": 1_200_000},
            ),
        ])
        self.assertEqual(classify.classify(g), "screenshots")

    def test_burst_same_device_within_window(self):
        g = _group([
            _asset(id="a", originalFileName="IMG_1001.HEIC",
                   fileCreatedAt="2025-06-01T12:00:00.000Z"),
            _asset(id="b", originalFileName="IMG_1002.HEIC",
                   fileCreatedAt="2025-06-01T12:00:02.000Z"),
            _asset(id="c", originalFileName="IMG_1003.HEIC",
                   fileCreatedAt="2025-06-01T12:00:04.500Z"),
        ])
        self.assertEqual(classify.classify(g), "burst")

    def test_burst_different_devices_is_edge_case(self):
        g = _group([
            _asset(id="a", originalFileName="apple_shot.heic",
                   exifInfo={"make": "Apple", "model": "iPhone 16 Pro",
                             "fileSizeInByte": 4_000_000}),
            _asset(id="b", originalFileName="sony_shot.arw",
                   exifInfo={"make": "Sony", "model": "A7 IV",
                             "fileSizeInByte": 5_000_000}),
        ])
        self.assertEqual(classify.classify(g), "edge_case")

    def test_burst_outside_window_is_edge_case(self):
        g = _group([
            _asset(id="a", originalFileName="IMG_1001.HEIC",
                   fileCreatedAt="2025-06-01T12:00:00.000Z"),
            _asset(id="b", originalFileName="IMG_1002.HEIC",
                   fileCreatedAt="2025-06-01T12:05:00.000Z"),
        ])
        self.assertEqual(classify.classify(g), "edge_case")

    def test_single_asset_group_is_edge_case(self):
        g = _group([_asset()])
        self.assertEqual(classify.classify(g), "edge_case")


class DominantKeeperTests(unittest.TestCase):
    def test_keeper_holds_majority_of_bytes(self):
        # Keeper 10MB, losers 2MB + 1MB + 0.5MB = 3.5MB total. Keeper dominates.
        g = _group(
            assets=[
                _asset(id="keep", originalFileName="a.heic",
                       exifInfo={"fileSizeInByte": 10_000_000}),
                _asset(id="l1", originalFileName="b.heic",
                       exifInfo={"fileSizeInByte": 2_000_000}),
                _asset(id="l2", originalFileName="c.heic",
                       exifInfo={"fileSizeInByte": 1_000_000}),
                _asset(id="l3", originalFileName="d.heic",
                       exifInfo={"fileSizeInByte": 500_000}),
            ],
            suggested=["keep"],
        )
        self.assertEqual(classify.classify(g), "dominant_keeper")

    def test_keeper_has_much_more_pixels(self):
        g = _group(
            assets=[
                _asset(id="keep", originalFileName="big.heic",
                       width=4032, height=3024,
                       exifInfo={"fileSizeInByte": 3_000_000}),
                _asset(id="l1", originalFileName="small.heic",
                       width=1024, height=768,
                       exifInfo={"fileSizeInByte": 2_000_000}),
            ],
            suggested=["keep"],
        )
        self.assertEqual(classify.classify(g), "dominant_keeper")

    def test_keeper_twice_filesize_of_largest_loser(self):
        g = _group(
            assets=[
                _asset(id="keep", originalFileName="big.heic",
                       width=2000, height=2000,
                       exifInfo={"fileSizeInByte": 4_000_000}),
                _asset(id="l1", originalFileName="mid.heic",
                       width=2000, height=2000,
                       exifInfo={"fileSizeInByte": 2_000_000}),
            ],
            suggested=["keep"],
        )
        self.assertEqual(classify.classify(g), "dominant_keeper")

    def test_similar_sizes_fall_through_to_edge_case(self):
        # Keeper 2.0MB, losers 1.5MB + 1.5MB. No rule fires:
        #   - keeper (2.0) < sum losers (3.0)
        #   - keeper pixels not 2× any loser
        #   - keeper filesize not 2× largest loser
        # Timestamps staggered beyond 5s so burst doesn't fire either.
        g = _group(
            assets=[
                _asset(id="keep", originalFileName="aaa.heic",
                       width=3000, height=2000,
                       fileCreatedAt="2025-06-01T12:00:00.000Z",
                       exifInfo={"make": "Apple", "model": "iPhone 16 Pro",
                                 "fileSizeInByte": 2_000_000}),
                _asset(id="l1", originalFileName="bbb.heic",
                       width=3000, height=2000,
                       fileCreatedAt="2025-06-01T12:00:02.000Z",
                       exifInfo={"make": "Apple", "model": "iPhone 16 Pro",
                                 "fileSizeInByte": 1_500_000}),
                _asset(id="l2", originalFileName="ccc.heic",
                       width=3000, height=2000,
                       fileCreatedAt="2025-06-01T12:10:00.000Z",
                       exifInfo={"make": "Apple", "model": "iPhone 16 Pro",
                                 "fileSizeInByte": 1_500_000}),
            ],
            suggested=["keep"],
        )
        self.assertEqual(classify.classify(g), "edge_case")

    def test_no_suggested_keeper_not_dominant(self):
        # Without a suggestion, dominant_keeper can't fire. Same device + same
        # time → burst fires first in the classify ordering.
        g = _group(
            assets=[
                _asset(id="a", originalFileName="x.heic",
                       exifInfo={"make": "Apple", "model": "iPhone 16 Pro",
                                 "fileSizeInByte": 10_000_000}),
                _asset(id="b", originalFileName="y.heic",
                       exifInfo={"make": "Apple", "model": "iPhone 16 Pro",
                                 "fileSizeInByte": 1_000_000}),
            ],
            suggested=[],
        )
        self.assertEqual(classify.classify(g), "burst")


class ReclaimBytesTests(unittest.TestCase):
    def test_reclaim_uses_suggested_keep(self):
        g = _group(
            assets=[
                _asset(id="keep", exifInfo={"fileSizeInByte": 5_000_000}),
                _asset(id="loser1", exifInfo={"fileSizeInByte": 3_000_000}),
                _asset(id="loser2", exifInfo={"fileSizeInByte": 2_000_000}),
            ],
            suggested=["keep"],
        )
        self.assertEqual(classify.reclaim_bytes(g), 5_000_000)

    def test_reclaim_fallback_keeps_largest(self):
        g = _group(
            assets=[
                _asset(id="a", exifInfo={"fileSizeInByte": 1_000_000}),
                _asset(id="b", exifInfo={"fileSizeInByte": 5_000_000}),
                _asset(id="c", exifInfo={"fileSizeInByte": 2_000_000}),
            ],
            suggested=[],
        )
        # Keeps b (5MB), loses a (1MB) + c (2MB) = 3MB reclaim.
        self.assertEqual(classify.reclaim_bytes(g), 3_000_000)


if __name__ == "__main__":
    unittest.main()
