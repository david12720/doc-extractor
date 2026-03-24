import io
import os
from pathlib import Path

import pypdfium2 as pdfium
from PIL import Image

from ..abstractions.file_preparator import FileConverter, PreparedFile
from ..config.settings import PDF_RENDER_DPI


class PdfToImageConverter(FileConverter):
    def __init__(self, dpi: int = PDF_RENDER_DPI):
        self._scale = dpi / 72.0

    def convert(self, input_files: list[Path]) -> list[PreparedFile]:
        results: list[PreparedFile] = []
        for path in input_files:
            _, suffix = os.path.splitext(str(path))
            suffix = suffix.lower()
            if suffix == ".pdf":
                results.extend(self._convert_pdf(path))
            elif suffix in (".png", ".jpg", ".jpeg"):
                results.append(self._convert_image(path))
            else:
                raise ValueError(f"Unsupported file type: {suffix}")
        return results

    def _convert_pdf(self, path: Path) -> list[PreparedFile]:
        pdf_bytes = path.read_bytes()
        doc = pdfium.PdfDocument(pdf_bytes)
        files: list[PreparedFile] = []
        for i in range(len(doc)):
            page = doc[i]
            bitmap = page.render(scale=self._scale)
            img = bitmap.to_pil()
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            files.append(PreparedFile(
                source_path=path,
                data=buf.getvalue(),
                mime_type="image/png",
                page_index=i,
            ))
        return files

    def _convert_image(self, path: Path) -> PreparedFile:
        img = Image.open(path)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return PreparedFile(
            source_path=path,
            data=buf.getvalue(),
            mime_type="image/png",
            page_index=0,
        )
