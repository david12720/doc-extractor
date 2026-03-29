# PaytollControl -- Architecture Decisions

## Why this architecture?

The project processes multiple document types ("features") that share the same pipeline but differ in data fields, prompts, and Excel mappings. The core pipeline lives in `libs/pdf-pipeline/` (package `pdf_pipeline`) as a shared library; this project consumes it and adds domain-specific features on top. Adding a new feature requires only adding a new subpackage -- zero changes to existing code (Open/Closed Principle).

## Key decisions

### 1. ABCs over duck typing
Every swappable component has an explicit ABC (defined in `pdf_pipeline.abstractions`). This makes contracts visible, enables IDE support, and catches integration errors early.

### 2. Feature as subpackage
Each feature is a self-contained directory with 5 files. This colocation makes features easy to find, understand, and delete.

### 3. Dependency Inversion
The core abstractions, implementations, config, and pipeline orchestration all live in `pdf_pipeline` (the library). This project owns only `features/` and `factories/`:

- `features/` depend only on `pdf_pipeline.abstractions` -- never on concrete implementations
- `factories/` is the only place that knows about concrete classes from `pdf_pipeline.implementations`
- `run.py` wires everything together via factories

```
run.py -> factories/ -> pdf_pipeline.implementations.*
                      -> pdf_pipeline.core.*
          features/  -> pdf_pipeline.abstractions.* (only abstractions)
```

### 4. JSON intermediate output
Pipeline outputs JSON, not Excel. This avoids file-locking issues and makes the extracted data portable. Excel mapping is a separate future step.

### 5. Image preprocessing pipeline
Scanned PDFs go through (handled by `pdf_pipeline`): PDF->PNG (300 DPI) -> Rotate (sideways detection via row/col variance) -> Deskew (angle sweep -5 deg to +5 deg) -> Line removal -> Enhance (contrast 4.0, sharpness 2.0). This chain dramatically improves LLM accuracy on faint handwriting.

### 5a. Optional OCR preprocessing
For documents with difficult handwriting (e.g., employment contracts), Cloud Vision OCR can run as a preprocessing step (`--ocr` flag). The OCR text is passed alongside the document to the LLM, which uses it as an authoritative reference for hard-to-read values. This hybrid approach combines Cloud Vision's accurate character recognition with the LLM's structural understanding. Controlled via `ocr_engine` on `FeatureConfig` -- defaults to None (disabled) so existing features are unaffected.

### 6. Fallback response saving
Raw LLM responses are saved to `cache/fallback/` before any post-processing. This prevents data loss if downstream steps fail. Additionally, extractors can attach `_llm_raw_text` to records -- the pipeline strips it and writes a `.llm_raw.txt` file next to the output JSON, so the raw LLM output and the post-processed result are side-by-side for debugging.

### 7. File-based cache and status
Simple JSON/text files for cache and status. No database needed. Enables resume capability -- if a run crashes, re-running skips completed stages.

### 8. Dual pipeline architecture
Two pipeline types coexist in `pdf_pipeline`: `FeaturePipeline` (image-centric: prepare -> chunk -> LLM extract all data) and `ExcelPipeline` (schema-centric: LLM detects columns once -> code extracts rows programmatically). The factory picks the right pipeline based on `FeatureConfig` vs `ExcelFeatureConfig`.

## Extension guide

### Adding a new LLM provider or preparation step (library-level)
These live in `libs/pdf-pipeline/`. Create a new class implementing `LanguageModel` or `PreparationStep` in `pdf_pipeline.implementations`, then wire it in the consumer's factory.

### Adding a new feature (this project)
Create `src/payroll_control/features/<name>/` with the 5-file recipe (see CLAUDE.md). Register it in `factories/factory.py:bootstrap()`. No changes to the library needed.

## Reference
Architecture ported from the tamtzit_rishu project's proven patterns (LanguageModel ABC, ExcelProcessor ABC, CostLogger, retry logic).
