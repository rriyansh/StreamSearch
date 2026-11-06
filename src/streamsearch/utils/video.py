"""Video utility helpers."""

from __future__ import annotations

from pathlib import Path

import cv2


def extract_frame(video_path: str, timestamp: float):
    """Extract a single frame at a given timestamp."""
    cap = cv2.VideoCapture(video_path)
    cap.set(cv2.CAP_PROP_POS_MSEC, timestamp * 1000)
    ret, frame = cap.read()
    cap.release()
    if not ret:
        return None
    return frame


def list_videos(directory: str) -> list[Path]:
    """List video files in a directory."""
    exts = {".mp4", ".avi", ".mov", ".mkv", ".webm"}
    return sorted(p for p in Path(directory).iterdir() if p.suffix.lower() in exts)
