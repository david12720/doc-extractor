# pdf-pipeline -- Architecture Decisions

## 1. ABCs over duck typing

Every swappable component has an explicit abstract base class (`LanguageModel`, `PreparationStep`, `CacheManager`, `CostLogger`, `OcrEngine`, etc.). This makes contracts visible in code, enables IDE autocompletion and type checking, and catches integration errors at instantiation time rather than at runtime deep inside the pipeline.

## 2. Dependency inversion

The dependency rule is strict:

```
core/            --> abstractions/ only
implementations/ --> abstractions/ + config/
```

`core/` and `implementations/` never import from each other. The pipeline orchestrators (`FeaturePipeline`, `ExcelPipeline`) receive all dependencies through their constructors -- they never instantiate concrete classes. The consumer application's factory layer is the only place that wires concrete implementations together.

## 3. Image preprocessing pipeline

Scanned PDF pages go through a fixed-order chain before reaching the LLM:

```
PDF --> PNG (300 DPI) --> Rotate --> Deskew --> Line Remove --> Enhance
```

The order matters:

1. **PDF to PNG** (300 DPI) -- rasterizes pages at high resolution. PNG is used instead of sending raw PDFs because orientation and preprocessing require pixel manipulation.
2. **Rotate** -- detects and corrects 90/180/270-degree rotation using row/column variance analysis. Must happen before deskew, which handles only small angles.
3. **Deskew** -- corrects small skew angles (-5 to +5 degrees) via angle sweep. Must happen after rotation (large-angle correction) and before line removal (which assumes roughly straight lines).
4. **Line Remove** -- removes horizontal and vertical lines from form-based documents. Must happen before enhancement so that contrast boosting does not darken the lines.
5. **Enhance** -- increases contrast (4.0x) and sharpness (2.0x) for faint handwriting. Runs last so it operates on clean, properly oriented images.

Each step implements the `PreparationStep` ABC, so new steps can be inserted or removed without changing the pipeline.

## 4. Why 40-page chunk size

LLM APIs have context limits and degrade on very large inputs. Sending one page per API call is wasteful (high latency, high cost from per-request overhead). 40 pages is a practical sweet spot: large enough to amortize API overhead and provide cross-page context, small enough to stay within token limits for most models.

## 5. Fallback response saving

Raw LLM responses are saved to `cache/fallback/` before any post-processing. If parsing or downstream steps fail, the raw response is preserved and can be reprocessed without re-calling the API. Additionally, extractors can attach `_llm_raw_text` to records -- the pipeline strips it and writes a `.llm_raw.txt` file next to the output JSON for debugging.

## 6. File-based cache and status

Cache and status use simple JSON and text files on disk. No database is required. This enables resume capability: re-running an already-extracted file hydrates records from the JSON cache and writes them to whatever output path the caller passes — no LLM call is made. The status file tracks per-stage success/failure for observability and debugging. Cache keys are derived from feature name and input file stems.

## 7. Dual pipeline architecture

Two pipeline types address fundamentally different extraction strategies:

- **FeaturePipeline** -- image-centric. Prepares images, chunks them, and sends to an LLM to extract all data. Used for scanned documents where the LLM must read content from images.
- **ExcelPipeline** -- schema-centric. Uses an LLM once to detect column mappings from header rows, then extracts data rows programmatically using a `SpreadsheetReader`. Used for structured spreadsheets where the data is machine-readable but the schema varies.

The consumer's factory selects the pipeline type based on `FeatureConfig` vs `ExcelFeatureConfig`.

## 8. Optional OCR preprocessing

For documents with difficult handwriting, Cloud Vision OCR can run as a preprocessing step. The OCR text is passed alongside the document images to the LLM, which uses it as an authoritative reference for hard-to-read characters. This hybrid approach combines OCR's character-level accuracy with the LLM's structural understanding. Controlled via the `ocr_engine` field on `FeatureConfig` -- defaults to `None` so existing features are unaffected.

## 9. JSON intermediate output

The pipeline outputs JSON, not Excel or any other format. This avoids file-locking issues, makes output portable and diffable, and keeps the extraction pipeline decoupled from any specific output format. Excel mapping, if needed, is a separate downstream step handled by the consumer.

## 10. Extension guide

### Adding a new LLM provider

1. Create `implementations/new_model.py` implementing the `LanguageModel` ABC.
2. Update the consumer's factory to instantiate it based on configuration.

### Adding a new preprocessing step

1. Create `implementations/new_step.py` implementing the `PreparationStep` ABC.
2. Insert it into the preparation steps list in the consumer's factory at the appropriate position in the chain.

### Adding a new OCR engine

1. Create `implementations/new_ocr.py` implementing the `OcrEngine` ABC.
2. Pass it via `ocr_engine` on `FeatureConfig` for features that need it.
