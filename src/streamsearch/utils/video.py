"""Video helpers."""

from pathlib import Path

import cv2


def video_info(path: str | Path) -> dict:
    cap = cv2.VideoCapture(str(path))
    try:
        return {
            "path": str(path),
            "fps": float(cap.get(cv2.CAP_PROP_FPS) or 0.0),
            "frame_count": int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0),
            "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 0),
            "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0),
            "duration_sec": (cap.get(cv2.CAP_PROP_FRAME_COUNT) / (cap.get(cv2.CAP_PROP_FPS) or 1.0)),
        }
    finally:
        cap.release()
