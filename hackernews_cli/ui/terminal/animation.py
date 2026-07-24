"""Small deterministic helpers for selection animation."""

import math


def selection_frames(start, target, max_frames=8):
    """Return bounded intermediate indexes ending exactly at target."""
    distance = target - start
    if distance == 0:
        return [target]

    frame_count = min(abs(distance), max_frames)
    return [
        start + math.trunc(distance * frame / frame_count)
        for frame in range(1, frame_count + 1)
    ]
