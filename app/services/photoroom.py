"""
Photoroom Image Editing API v2 client.

Docs: https://docs.photoroom.com/image-editing-api-plus-plan/quickstart-guide
Endpoint: POST https://image-api.photoroom.com/v2/edit
Auth: x-api-key header

This module handles:
  - Resizing input to max 3000px long edge at JPEG quality 92 before upload
    (runs in a thread-pool executor — PIL is CPU-bound and must not block the event loop)
  - Calling Photoroom with the correct background params
  - AI shadow (shadow.mode=ai.soft)
  - Returning PNG bytes — lossless, ready to save to gallery
  - Per-stage timing (resize_ms, photoroom_ms, total_ms) returned alongside the image
"""

import asyncio
import io
import logging
import time
from pathlib import Path

import httpx
from PIL import Image

from app.config import settings
from app.services.backgrounds import get_background, backgrounds_dir

logger = logging.getLogger(__name__)

PHOTOROOM_API_URL = "https://image-api.photoroom.com/v2/edit"
REQUEST_TIMEOUT_S = 45.0


def _resize_to_max(image_bytes: bytes, max_long_edge: int) -> bytes:
    """
    Resize so longest edge <= max_long_edge.
    Returns resized JPEG bytes at quality 92.
    If already within limit, returns original bytes unchanged.
    """
    img = Image.open(io.BytesIO(image_bytes))

    # Flatten alpha before JPEG encode (JPEG has no alpha channel)
    if img.mode in ("RGBA", "LA", "P"):
        background = Image.new("RGB", img.size, (255, 255, 255))
        if img.mode == "P":
            img = img.convert("RGBA")
        background.paste(img, mask=img.split()[-1] if img.mode == "RGBA" else None)
        img = background
    elif img.mode != "RGB":
        img = img.convert("RGB")

    w, h = img.size
    long_edge = max(w, h)

    if long_edge <= max_long_edge:
        return image_bytes  # no-op, return original

    scale = max_long_edge / long_edge
    new_w = max(1, round(w * scale))
    new_h = max(1, round(h * scale))
    img = img.resize((new_w, new_h), Image.LANCZOS)

    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=92, subsampling=0)
    logger.debug("Resized %dx%d → %dx%d", w, h, new_w, new_h)
    return buf.getvalue()


class ProcessingTimings:
    """Per-stage wall-clock timings for a single process_image call."""
    def __init__(self, resize_ms: int, photoroom_ms: int, total_ms: int):
        self.resize_ms = resize_ms
        self.photoroom_ms = photoroom_ms
        self.total_ms = total_ms

    def __str__(self) -> str:
        return (
            f"resize={self.resize_ms}ms "
            f"photoroom={self.photoroom_ms}ms "
            f"total={self.total_ms}ms"
        )


async def process_image(image_bytes: bytes, background_id: str) -> tuple[bytes, ProcessingTimings]:
    """
    Send image to Photoroom, return (PNG bytes, timings).

    Raises:
        ValueError: unknown background_id
        TimeoutError: Photoroom call exceeded REQUEST_TIMEOUT_S
        RuntimeError: Photoroom API error (includes status code + body excerpt)
    """
    t_start = time.monotonic()

    bg = get_background(background_id)
    if bg is None:
        raise ValueError(f"Unknown background_id: {background_id!r}")

    # 1. Resize before upload — run in thread pool so PIL doesn't block the event loop
    loop = asyncio.get_event_loop()
    resized = await loop.run_in_executor(
        None, _resize_to_max, image_bytes, settings.max_long_edge_px
    )
    t_after_resize = time.monotonic()
    resize_ms = round((t_after_resize - t_start) * 1000)

    logger.info(
        "Sending to Photoroom: %d bytes → resized %d bytes, bg=%s (resize=%dms)",
        len(image_bytes),
        len(resized),
        background_id,
        resize_ms,
    )

    # 2. Build request
    data: dict[str, str] = {
        "removeBackground": "true",
        "export.format": "png",        # lossless output, no compression artefacts
        "shadow.mode": "ai.soft",      # realistic AI shadow under the car
    }

    files: dict = {
        "imageFile": ("photo.jpg", resized, "image/jpeg"),
    }

    # Background: prefer custom image file, fall back to solid colour
    bg_image_path: str | None = bg.get("image_path")
    if bg_image_path:
        full_path = backgrounds_dir() / bg_image_path
        if full_path.exists():
            files["background.imageFile"] = (
                full_path.name,
                full_path.read_bytes(),
                "image/png",
            )
        else:
            logger.warning("Background image not found: %s — falling back to colour", full_path)
            data["background.color"] = bg.get("color", "EBEBEB")
    elif "color" in bg:
        data["background.color"] = bg["color"]

    headers = {
        "x-api-key": settings.photoroom_api_key,
        "Accept": "image/png",
    }

    # 3. Call Photoroom
    t_before_photoroom = time.monotonic()
    async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT_S) as client:
        try:
            response = await client.post(
                PHOTOROOM_API_URL,
                headers=headers,
                data=data,
                files=files,
            )
        except httpx.TimeoutException:
            raise TimeoutError(
                f"Photoroom did not respond within {REQUEST_TIMEOUT_S:.0f}s — try again"
            )

    t_end = time.monotonic()
    photoroom_ms = round((t_end - t_before_photoroom) * 1000)
    total_ms = round((t_end - t_start) * 1000)

    if response.status_code != 200:
        body_excerpt = response.text[:600]
        raise RuntimeError(
            f"Photoroom API returned {response.status_code}: {body_excerpt}"
        )

    result = response.content
    timings = ProcessingTimings(resize_ms=resize_ms, photoroom_ms=photoroom_ms, total_ms=total_ms)
    logger.info("Photoroom result: %d bytes PNG — %s", len(result), timings)
    return result, timings
