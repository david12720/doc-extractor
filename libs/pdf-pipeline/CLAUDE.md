# pdf-pipeline — Claude Code Instructions

## Overview

Generic PDF-to-JSON extraction pipeline via LLM. Takes PDF files, converts pages to images, preprocesses them, sends to an LLM in chunks, and returns raw text. **Knows nothing about any specific domain** — consumers provide prompts and parse results.

## File Architecture

```
src/pdf_pipeline/
├── __init__.py
├── abstractions/
│   ├── __init__.py
│   ├── cache_manager.py       # CacheManager ABC
│   ├── cost_logger.py         # CostLogger ABC
│   ├── data_extractor.py      # DataExtractor ABC
│   ├── excel_mapper.py        # ExcelMapper ABC
│   ├── file_preparator.py     # PreparationStep ABC, FileConverter ABC
│   ├── language_model.py      # LanguageModel ABC
│   ├── ocr_engine.py          # OcrEngine ABC
│   ├── schema_detector.py     # SchemaDetector ABC
│   ├── spreadsheet_reader.py  # SpreadsheetReader ABC
│   └── status_tracker.py      # StatusTracker ABC
├── config/
│   ├── __init__.py
│   ├── pricing.py             # Per-model token pricing
│   └── settings.py            # DPI, chunk size, enhancement params
├── core/
│   ├── __init__.py
│   ├── excel_pipeline.py      # ExcelPipeline orchestrator
│   ├── feature_registry.py    # FeatureRegistry, FeatureConfig, ExcelFeatureConfig
│   ├── file_key.py            # Cache/status key builder
│   └── pipeline.py            # FeaturePipeline orchestrator
└── implementations/
    ├── __init__.py
    ├── cloud_vision_ocr.py    # CloudVisionOcr (OcrEngine)
    ├── csv_cost_logger.py     # CsvCostLogger (CostLogger)
    ├── file_cache_manager.py  # FileCacheManager (CacheManager)
    ├── gemini_model.py        # GeminiModel (LanguageModel)
    ├── image_enhancer.py      # ImageEnhancer (PreparationStep)
    ├── json_status_tracker.py # JsonStatusTracker (StatusTracker)
    ├── line_remover.py        # LineRemover (PreparationStep)
    ├── llm_schema_detector.py # LlmSchemaDetector (SchemaDetector)
    ├── openpyxl_reader.py     # OpenpyxlReader (SpreadsheetReader)
    ├── page_deskewer.py       # PageDeskewer (PreparationStep)
    ├── page_rotator.py        # PageRotator (PreparationStep)
    ├── pdf_to_image_converter.py # PdfToImageConverter (FileConverter)
    └── xlwings_mapper.py      # XlwingsMapper (ExcelMapper)

tests/
├── unit/
│   ├── test_csv_cost_logger.py
│   ├── test_excel_pipeline.py
│   ├── test_feature_registry.py
│   ├── test_file_cache_manager.py
│   ├── test_json_status_tracker.py
│   ├── test_llm_schema_detector.py
│   └── test_preparation_pipeline.py
```

## Dependency Rule

```
core/ → abstractions/ only
implementations/ → abstractions/ + config/
```

**core/ and implementations/ NEVER import from each other's internals.**

## Image Preparation Pipeline

PDF pages go through this pipeline before LLM extraction:

1. **PdfToImageConverter** — renders each PDF page to PNG at 300 DPI
2. **PageRotator** — detects and corrects rotation
3. **PageDeskewer** — corrects small skew angles
4. **ImageEnhancer** — increases contrast and sharpness
5. **LineRemover** — removes horizontal/vertical lines from forms

## Rules

1. **Never import from consumer applications** — no domain-specific code
2. **Never depend on a specific data schema** — receive a prompt, return raw LLM text
3. **New preprocessing steps** go behind the PreparationStep ABC
4. **New LLM providers** go behind the LanguageModel ABC
5. **Default chunk size: 40 pages** — always send documents in chunks, never per-page

## Commands

- Run tests: `python -m pytest tests/ -v`
- Install (editable): `pip install -e .`
