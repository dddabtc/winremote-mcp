"""Screen recording — capture frames and produce an animated GIF."""

from __future__ import annotations

import base64
import io
import time

from PIL import ImageGrab


def record_screen(
    duration: float = 3.0,
    fps: int = 5,
    left: int | None = None,
    top: int | None = None,
    right: int | None = None,
    bottom: int | None = None,
    max_width: int = 800,
) -> str:
    """Record the screen for *duration* seconds at *fps* and return a base64 GIF.

    Args:
        duration: Recording length in seconds (max 10).
        fps: Frames per second (max 10).
        left/top/right/bottom: Optional region to capture.
        max_width: Resize frames to this max width.

    Returns:
        Base64-encoded GIF data.
    """
    duration = min(max(duration, 0.5), 10.0)
    fps = min(max(fps, 1), 10)
    interval = 1.0 / fps
    total_frames = int(duration * fps)

    bbox = None
    if left is not None and top is not None and right is not None and bottom is not None:
        bbox = (left, top, right, bottom)

    frames = []
    start = time.monotonic()
    for i in range(total_frames):
        target_time = start + i * interval
        now = time.monotonic()
        if now < target_time:
            time.sleep(target_time - now)

        img = ImageGrab.grab(bbox=bbox)
        # Resize if needed
        if img.width > max_width:
            ratio = max_width / img.width
            new_size = (max_width, int(img.height * ratio))
            img = img.resize(new_size)
        frames.append(img)

    if not frames:
        raise RuntimeError("No frames captured")

    # Create GIF
    buf = io.BytesIO()
    frame_duration_ms = int(1000 / fps)
    frames[0].save(
        buf,
        format="GIF",
        save_all=True,
        append_images=frames[1:],
        duration=frame_duration_ms,
        loop=0,
        optimize=True,
    )
    return base64.b64encode(buf.getvalue()).decode()
