# pdf-pipeline

A generic PDF-to-JSON extraction pipeline powered by LLMs. Takes PDF files, converts pages to images, runs a configurable preprocessing chain (rotation, deskew, line removal, contrast enhancement), sends images to an LLM in 40-page chunks, and returns structured JSON. The library is domain-agnostic -- consumers provide their own prompts, data models, and parsing logic.

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
  v
LLM extraction (via LanguageModel ABC)
  |
  v
JSON output
```

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
