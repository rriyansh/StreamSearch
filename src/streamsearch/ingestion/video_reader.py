"""Video reading utilities using OpenCV."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, List

import cv2
import numpy as np


@dataclass
class Frame:
    timestamp: float
    index: int
    image: np.ndarray


class VideoReader:
    """Read frames from a video file."""

    def __init__(self, path: str, sample_rate: float = 1.0) -> None:
        self.path = path
        self.sample_rate = sample_rate
        self.cap = cv2.VideoCapture(path)
        if not self.cap.isOpened():
            raise ValueError(f"Cannot open video: {path}")
        self.fps = self.cap.get(cv2.CAP_PROP_FPS) or 30.0
        self.frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
        self.duration = self.frame_count / self.fps if self.fps else 0.0

    def __iter__(self) -> Iterator[Frame]:
        index = 0
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if index % max(1, int(round(1.0 / self.sample_rate))) == 0:
                timestamp = index / self.fps if self.fps else 0.0
                yield Frame(timestamp=timestamp, index=index, image=frame)
            index += 1
        self.cap.release()

    def __enter__(self) -> "VideoReader":
        return self

    def __exit__(self, *exc) -> None:
        self.cap.release()

    def sample_frames(self, timestamps: List[float]) -> List[Frame]:
        """Read specific frames at given timestamps."""
        frames: List[Frame] = []
        for timestamp in timestamps:
            self.cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
            ret, image = self.cap.read()
            if ret:
                frames.append(Frame(timestamp=timestamp, index=len(frames), image=image))
        return frames
