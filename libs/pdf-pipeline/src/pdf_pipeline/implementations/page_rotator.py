import io

import numpy as np
from PIL import Image

from ..abstractions.file_preparator import PreparationStep, PreparedFile

SIDEWAYS_CONTENT_RATIO = 3.0


class PageRotator(PreparationStep):
    """Detects and corrects page rotation issues:
    1. Landscape pages (width > height) with blank margins -> rotate 90 CW
    2. Portrait pages with sideways content (vertical text lines) -> rotate 90 CW
    """

    def process(self, files: list[PreparedFile]) -> list[PreparedFile]:
        return [self._maybe_rotate(f) for f in files]

    def _maybe_rotate(self, prepared: PreparedFile) -> PreparedFile:
        img = Image.open(io.BytesIO(prepared.data))
        w, h = img.size

        if w > h:
            img, rotated = self._try_landscape_fix(img)
            if rotated:
                return self._save(img, prepared, "rotated_90")
        else:
            img, rotated = self._try_sideways_content_fix(img)
            if rotated:
                return self._save(img, prepared, "rotated_90_sideways")

        return prepared

    def _try_landscape_fix(self, img: Image.Image) -> tuple[Image.Image, bool]:
        w, h = img.size
        gray = img.convert("L")
        top_min = gray.crop((0, 0, w, max(1, int(h * 0.15)))).getextrema()[0]
        bottom_min = gray.crop((0, int(h * 0.85), w, h)).getextrema()[0]

        if top_min > 200 and bottom_min > 200:
            return img.rotate(90, expand=True), True
        return img, False

    def _try_sideways_content_fix(self, img: Image.Image) -> tuple[Image.Image, bool]:
        gray = np.array(img.convert("L"))
        binary = gray < 180

        row_var = float(np.var(np.sum(binary, axis=1)))
        col_var = float(np.var(np.sum(binary, axis=0)))

        if row_var == 0 and col_var == 0:
            return img, False

        ratio = col_var / max(row_var, 1)
        if ratio > SIDEWAYS_CONTENT_RATIO:
            return img.rotate(90, expand=True), True

        return img, False

    def _save(self, img: Image.Image, prepared: PreparedFile, label: str) -> PreparedFile:
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return PreparedFile(
            source_path=prepared.source_path,
            data=buf.getvalue(),
            mime_type=prepared.mime_type,
            page_index=prepared.page_index,
            metadata={**prepared.metadata, label: True},
        )
