"""Unit tests for VisionThumbnailSelectorAdapter."""

import os
import shutil
import tempfile
import cv2
import numpy as np
import pytest

from module.video_rag.infra.thumbnail_selector.vision_adapter import (
    VisionThumbnailSelectorAdapter,
)


@pytest.fixture
def temp_images_dir():
    d = tempfile.mkdtemp(prefix="test_thumbs_")
    yield d
    shutil.rmtree(d, ignore_errors=True)


def create_test_image(path: str, brightness: int, sharp: bool) -> str:
    """Create a synthetic test image with controllable brightness and sharpness."""
    img = np.full((100, 100, 3), brightness, dtype=np.uint8)
    if sharp:
        # Draw high-contrast grid lines to generate high Laplacian variance
        for i in range(0, 100, 10):
            cv2.line(img, (i, 0), (i, 100), (255 - brightness, 255 - brightness, 255 - brightness), 2)
            cv2.line(img, (0, i), (100, i), (255 - brightness, 255 - brightness, 255 - brightness), 2)
    cv2.imwrite(path, img)
    return path


async def test_select_best_frame_filters_dark_and_selects_sharpest(temp_images_dir):
    # Image 1: Too dark (brightness=10, no bright lines)
    dark_path = os.path.join(temp_images_dir, "frame_dark.jpg")
    create_test_image(dark_path, brightness=10, sharp=False)

    # Image 2: Normal brightness but blurry (flat gray)
    blur_path = os.path.join(temp_images_dir, "frame_blur.jpg")
    create_test_image(blur_path, brightness=128, sharp=False)

    # Image 3: Normal brightness and sharp (grid)
    sharp_path = os.path.join(temp_images_dir, "frame_sharp.jpg")
    create_test_image(sharp_path, brightness=128, sharp=True)

    adapter = VisionThumbnailSelectorAdapter(fallback_mode=True)
    best = await adapter.select_best_frame(
        [dark_path, blur_path, sharp_path],
        video_context="Test context",
    )

    assert best == sharp_path


async def test_select_best_frame_empty_list():
    adapter = VisionThumbnailSelectorAdapter()
    best = await adapter.select_best_frame([])
    assert best == ""


async def test_select_best_frame_single_item(temp_images_dir):
    p = os.path.join(temp_images_dir, "single.jpg")
    create_test_image(p, brightness=128, sharp=False)
    adapter = VisionThumbnailSelectorAdapter()
    best = await adapter.select_best_frame([p])
    assert best == p
