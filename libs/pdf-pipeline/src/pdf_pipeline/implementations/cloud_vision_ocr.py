import io
from pathlib import Path

import pypdfium2 as pdfium
from google.cloud import vision

from ..abstractions.cost_logger import CostLogger
from ..abstractions.ocr_engine import OcrEngine
from ..config.settings import PDF_RENDER_DPI

OCR_RENDER_DPI = PDF_RENDER_DPI
SERVICE_NAME = "cloud-vision-ocr"


class CloudVisionOcr(OcrEngine):
    """OCR engine using Google Cloud Vision DOCUMENT_TEXT_DETECTION."""

    def __init__(self, api_key: str, cost_logger: CostLogger | None = None, dpi: int = OCR_RENDER_DPI):
        self._client = vision.ImageAnnotatorClient(
            client_options={"api_key": api_key},
        )
        self._scale = dpi / 72.0
        self._cost_logger = cost_logger

    def ocr_pages(self, pdf_path: Path) -> list[str]:
        pdf_bytes = pdf_path.read_bytes()
        doc = pdfium.PdfDocument(pdf_bytes)
        results: list[str] = []

        for i in range(len(doc)):
            page = doc[i]
            bitmap = page.render(scale=self._scale)
            img = bitmap.to_pil()

            buf = io.BytesIO()
            img.save(buf, format="PNG")
            png_bytes = buf.getvalue()

            text = self._ocr_image(png_bytes)
            results.append(text)
            print(f"[OCR] Page {i + 1}: {len(text)} chars")

        if self._cost_logger:
            try:
                self._cost_logger.log_pages(SERVICE_NAME, len(results))
            except Exception as e:
                print(f"[WARNING] OCR cost logging failed: {e}")

        return results

    def _ocr_image(self, image_bytes: bytes) -> str:
        image = vision.Image(content=image_bytes)
        response = self._client.document_text_detection(image=image)

        if response.error.message:
            raise RuntimeError(f"Cloud Vision error: {response.error.message}")

        if response.full_text_annotation:
            return response.full_text_annotation.text
        return ""
