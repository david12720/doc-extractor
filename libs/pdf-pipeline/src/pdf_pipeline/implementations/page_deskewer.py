import io
import math

import numpy as np
from PIL import Image

from ..abstractions.file_preparator import PreparationStep, PreparedFile

MAX_SKEW_DEGREES = 5.0
ANGLE_STEP = 0.1
MIN_SKEW_DEGREES = 0.3


class PageDeskewer(PreparationStep):
    """Detects and corrects small skew angles from diagonal scanning."""

    def process(self, files: list[PreparedFile]) -> list[PreparedFile]:
        return [self._maybe_deskew(f) for f in files]

    def _maybe_deskew(self, prepared: PreparedFile) -> PreparedFile:
        img = Image.open(io.BytesIO(prepared.data))
        angle = self._detect_skew(img)

        if abs(angle) < MIN_SKEW_DEGREES:
            return prepared

        deskewed = img.rotate(angle, expand=True, fillcolor=(255, 255, 255))
        buf = io.BytesIO()
        deskewed.save(buf, format="PNG")
        return PreparedFile(
            source_path=prepared.source_path,
            data=buf.getvalue(),
            mime_type=prepared.mime_type,
            page_index=prepared.page_index,
            metadata={**prepared.metadata, "deskewed": True, "skew_angle": angle},
        )

    def _detect_skew(self, img: Image.Image) -> float:
        gray = np.array(img.convert("L"))
        steps = int(MAX_SKEW_DEGREES / ANGLE_STEP)

        best_angle = 0.0
        best_score = 0.0
        for step in range(-steps, steps + 1):
            angle = step * ANGLE_STEP
            rotated = img.convert("L").rotate(angle, expand=False, fillcolor=255)
            row_sums = np.sum(np.array(rotated) < 128, axis=1)
            score = float(np.var(row_sums))
            if score > best_score:
                best_score = score
                best_angle = angle

        return best_angle
