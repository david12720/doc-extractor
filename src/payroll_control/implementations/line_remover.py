import io

import numpy as np
from PIL import Image

from ..abstractions.file_preparator import PreparationStep, PreparedFile

MIN_LINE_LENGTH_RATIO = 0.05
LINE_THICKNESS = 3


class LineRemover(PreparationStep):
    """Removes horizontal and vertical lines from scanned documents.

    Table lines and underlines can interfere with handwriting recognition
    by merging visually with handwritten digits (e.g., '1' looks like '4').
    """

    def __init__(
        self,
        min_line_length_ratio: float = MIN_LINE_LENGTH_RATIO,
        line_thickness: int = LINE_THICKNESS,
    ):
        self._min_line_length_ratio = min_line_length_ratio
        self._line_thickness = line_thickness

    def process(self, files: list[PreparedFile]) -> list[PreparedFile]:
        return [self._remove_lines(f) for f in files]

    def _remove_lines(self, prepared: PreparedFile) -> PreparedFile:
        img = Image.open(io.BytesIO(prepared.data)).convert("L")
        arr = np.array(img)

        binary = (arr < 128).astype(np.uint8)

        cleaned = self._remove_horizontal_lines(binary, arr.shape[1])
        cleaned = self._remove_vertical_lines(cleaned, arr.shape[0])

        result_arr = np.where(cleaned, arr, np.uint8(255))
        result = Image.fromarray(result_arr).convert("RGB")

        buf = io.BytesIO()
        result.save(buf, format="PNG")
        return PreparedFile(
            source_path=prepared.source_path,
            data=buf.getvalue(),
            mime_type=prepared.mime_type,
            page_index=prepared.page_index,
            metadata={**prepared.metadata, "lines_removed": True},
        )

    def _remove_horizontal_lines(self, binary: np.ndarray, width: int) -> np.ndarray:
        min_length = int(width * self._min_line_length_ratio)
        result = binary.copy()
        for row_idx in range(binary.shape[0]):
            row = binary[row_idx]
            run_start = None
            for col_idx in range(len(row) + 1):
                pixel = row[col_idx] if col_idx < len(row) else 0
                if pixel == 1 and run_start is None:
                    run_start = col_idx
                elif pixel == 0 and run_start is not None:
                    run_length = col_idx - run_start
                    if run_length >= min_length:
                        thickness = self._measure_thickness_vertical(binary, row_idx, run_start, col_idx)
                        if thickness <= self._line_thickness:
                            result[row_idx, run_start:col_idx] = 0
                    run_start = None
        return result

    def _remove_vertical_lines(self, binary: np.ndarray, height: int) -> np.ndarray:
        min_length = int(height * self._min_line_length_ratio)
        result = binary.copy()
        for col_idx in range(binary.shape[1]):
            col = binary[:, col_idx]
            run_start = None
            for row_idx in range(len(col) + 1):
                pixel = col[row_idx] if row_idx < len(col) else 0
                if pixel == 1 and run_start is None:
                    run_start = row_idx
                elif pixel == 0 and run_start is not None:
                    run_length = row_idx - run_start
                    if run_length >= min_length:
                        thickness = self._measure_thickness_horizontal(binary, col_idx, run_start, row_idx)
                        if thickness <= self._line_thickness:
                            result[run_start:row_idx, col_idx] = 0
                    run_start = None
        return result

    def _measure_thickness_vertical(
        self, binary: np.ndarray, row: int, col_start: int, col_end: int
    ) -> int:
        """Measure how thick a horizontal line is by checking rows above/below."""
        thickness = 1
        for direction in (-1, 1):
            r = row + direction
            while 0 <= r < binary.shape[0]:
                segment = binary[r, col_start:col_end]
                if segment.mean() > 0.5:
                    thickness += 1
                    r += direction
                else:
                    break
        return thickness

    def _measure_thickness_horizontal(
        self, binary: np.ndarray, col: int, row_start: int, row_end: int
    ) -> int:
        """Measure how thick a vertical line is by checking columns left/right."""
        thickness = 1
        for direction in (-1, 1):
            c = col + direction
            while 0 <= c < binary.shape[1]:
                segment = binary[row_start:row_end, c]
                if segment.mean() > 0.5:
                    thickness += 1
                    c += direction
                else:
                    break
        return thickness
