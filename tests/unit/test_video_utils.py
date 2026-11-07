import numpy as np

from streamsearch.utils.image import bgr_to_pil, pil_to_bgr


def test_roundtrip():
    bgr = np.zeros((10, 10, 3), dtype=np.uint8)
    bgr[:, :, 1] = 255  # green channel
    pil = bgr_to_pil(bgr)
    back = pil_to_bgr(pil)
    assert np.array_equal(bgr, back)
