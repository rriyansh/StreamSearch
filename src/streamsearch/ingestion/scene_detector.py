"""Scene detection based on frame difference."""

from __future__ import annotations

from typing import List

import cv2
import numpy as np


class SceneDetector:
    """Detect scene boundaries using absolute frame difference."""

    def __init__(self, threshold: float = 0.3, min_duration: float = 2.0) -> None:
        self.threshold = threshold
        self.min_duration = min_duration

    def detect(self, frames) -> List[dict]:
        """Return a list of scene segments with start/end timestamps."""
        scenes: List[dict] = []
        if not frames:
            return scenes

        prev_gray = None
        scene_start = frames[0].timestamp

        for frame in frames:
            gray = cv2.cvtColor(frame.image, cv2.COLOR_RGB2GRAY)
            if prev_gray is not None:
                diff = cv2.absdiff(prev_gray, gray)
                score = float(diff.mean()) / 255.0
                if score > self.threshold and (frame.timestamp - scene_start) >= self.min_duration:
                    scenes.append({"start": scene_start, "end": frame.timestamp, "score": score})
                    scene_start = frame.timestamp
            prev_gray = gray

        scenes.append({"start": scene_start, "end": frames[-1].timestamp, "score": 0.0})
        return scenes
