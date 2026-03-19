import io

from PIL import Image, ImageEnhance

from ..abstractions.file_preparator import PreparationStep, PreparedFile

DEFAULT_CONTRAST = 4.0
DEFAULT_SHARPNESS = 2.0


class ImageEnhancer(PreparationStep):
    """Enhances image contrast and sharpness to improve LLM readability of faint handwriting."""

    def __init__(self, contrast: float = DEFAULT_CONTRAST, sharpness: float = DEFAULT_SHARPNESS):
        self._contrast = contrast
        self._sharpness = sharpness

    def process(self, files: list[PreparedFile]) -> list[PreparedFile]:
        return [self._enhance(f) for f in files]

    def _enhance(self, prepared: PreparedFile) -> PreparedFile:
        img = Image.open(io.BytesIO(prepared.data))
        img = ImageEnhance.Contrast(img).enhance(self._contrast)
        img = ImageEnhance.Sharpness(img).enhance(self._sharpness)

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return PreparedFile(
            source_path=prepared.source_path,
            data=buf.getvalue(),
            mime_type=prepared.mime_type,
            page_index=prepared.page_index,
            metadata={**prepared.metadata, "enhanced": True},
        )
