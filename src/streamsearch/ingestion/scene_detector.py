"""Detect scene changes so we do not embed duplicate frames."""

import numpy as np

from ..logging_config import get_logger
from .video_reader import Frame

logger = get_logger(__name__)


class SceneDetector:
    """
    Lightweight histogram-difference detector.

    A frame is considered a *new scene* if the correlation distance between
    consecutive frames' HSV histograms exceeds ``threshold``.
    """

    def __init__(self, threshold: float = 30.0) -> None:
        self.threshold = threshold
        self._last_hist: np.ndarray | None = None

    def is_new_scene(self, frame: Frame) -> bool:
        import cv2

        hsv = cv2.cvtColor(frame.image, cv2.COLOR_BGR2HSV)
        hist = cv2.calcHist([hsv], [0, 1], None, [32, 32], [0, 180, 0, 256])
        cv2.normalize(hist, hist, 0, 1, cv2.NORM_MINMAX)

        if self._last_hist is None:
            self._last_hist = hist
            return True

        diff = float(cv2.compareHist(self._last_hist, hist, cv2.HISTCMP_CORREL))
        self._last_hist = hist
        # HISTCMP_CORREL ∈ [-1, 1]; 1 = identical. Convert to a distance-like score.
        distance = (1.0 - diff) * 100.0
        return distance > self.threshold
