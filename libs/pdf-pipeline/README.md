# pdf-pipeline

A generic PDF-to-JSON extraction pipeline powered by LLMs. Takes PDF files, converts pages to images, preprocesses them, and sends them to an LLM in chunks for structured extraction. Optionally runs an OCR engine first and passes the extracted text alongside the images, giving the LLM both visual and textual input for difficult handwriting. The library is domain-agnostic -- consumers provide their own prompts, data models, and parsing logic.

## Installation

```bash
pip install -e .

# With dev dependencies (pytest)
pip install -e ".[dev]"
```

## Architecture

```
pdf_pipeline/
  abstractions/     ABCs defining all contracts (LanguageModel, DataExtractor,
                    PreparationStep, CacheManager, CostLogger, OcrEngine, ...)

  core/             Pipeline orchestration (FeaturePipeline, ExcelPipeline,
                    FeatureRegistry, file key builder)

  implementations/  Concrete classes (Gemini, Cloud Vision OCR, image
                    preprocessing steps, file cache, CSV cost logger, ...)

  config/           Settings (model names, chunk size, DPI) and pricing
```

### Dependency rule

```
core/            --> abstractions/ only
implementations/ --> abstractions/ + config/
```

`core/` and `implementations/` never import from each other. Consumer applications wire everything together in their own factory layer.

### Processing flow

```
Input PDF
  |
  v
PDF --> PNG (300 DPI) --> Rotate --> Deskew --> Line Remove --> Enhance
  |
  v
Chunk images (40 pages per chunk)
  |
  +--[optional OCR]--------> OCR engine (e.g. Cloud Vision)
  |                               |
  |                         OCR text per page
  |                               |
  +<------------------------------+
  |  images + OCR text (if enabled)
  v
LLM extraction (via LanguageModel ABC)
  |
  v
JSON output
```

**PDF → PNG (300 DPI):** Rasterizes pages at high resolution. Images are used instead of raw PDF bytes so that orientation and preprocessing can be applied before the LLM sees them.

**Rotate → Deskew → Line Remove → Enhance:** Preprocessing chain applied to each image before extraction.
- *Rotate* — corrects 90/180/270° rotation using variance analysis. Must run before deskew, which only handles small angles.
- *Deskew* — corrects small skew (±5°) common in scanned documents. Runs after rotation, before line removal (which assumes roughly straight lines).
- *Line Remove* — strips horizontal/vertical form lines that would otherwise confuse the LLM. Runs before enhancement so contrast boosting doesn't darken the lines further.
- *Enhance* — boosts contrast and sharpness for faint handwriting. Runs last, on a clean oriented image.

**Chunk (40 pages):** Groups images into 40-page batches before sending to the LLM. Sending one page per call is slow and expensive; sending the full document at once risks hitting context limits. 40 pages is a practical sweet spot that provides cross-page context while staying within model limits.

**OCR (optional):** Runs a dedicated OCR engine (e.g. Cloud Vision) on the images and passes the extracted text alongside them to the LLM. The LLM receives both visual and textual input, using OCR as an authoritative reference for hard-to-read characters. Controlled per-feature via `FeatureConfig.ocr_engine`.

**LLM extraction:** The LLM receives the chunk images (and OCR text if enabled) with a consumer-supplied prompt and returns structured text, which the consumer's `DataExtractor` parses into typed records.

## Usage

Consumer applications import from three layers:

```python
# Abstractions (for defining features)
from pdf_pipeline.abstractions import DataExtractor, ExcelMapper, LanguageModel

# Core (for pipeline orchestration and feature registration)
from pdf_pipeline.core.pipeline import FeaturePipeline
from pdf_pipeline.core.feature_registry import FeatureRegistry, FeatureConfig

# Implementations (only in the factory layer)
from pdf_pipeline.implementations.gemini_model import GeminiModel
from pdf_pipeline.implementations.pdf_to_image_converter import PdfToImageConverter
```

Features are registered via `FeatureRegistry` and run through either `FeaturePipeline` (for image-based extraction) or `ExcelPipeline` (for spreadsheet schema detection).

## Running Tests

```bash
python -m pytest tests/ -v
```

## Architecture Decisions

See [CONTEXT.md](CONTEXT.md) for detailed rationale behind the design choices.
