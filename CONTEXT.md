# PaytollControl — Architecture Decisions

## Why this architecture?

The project processes multiple document types ("features") that share the same pipeline but differ in data fields, prompts, and Excel mappings. The architecture ensures adding a new feature requires only adding a new subpackage — zero changes to existing code (Open/Closed Principle).

## Key decisions

### 1. ABCs over duck typing
Every swappable component has an explicit ABC. This makes contracts visible, enables IDE support, and catches integration errors early.

### 2. Feature as subpackage
Each feature is a self-contained directory with 5 files. This colocation makes features easy to find, understand, and delete.

### 3. Dependency Inversion
- `core/` and `features/` depend only on `abstractions/`
- `implementations/` depend on `abstractions/` + external libraries
- `factories/` is the only place that knows about concrete classes

### 4. JSON intermediate output
Pipeline outputs JSON, not Excel. This avoids file-locking issues and makes the extracted data portable. Excel mapping is a separate future step.

### 5. Image preprocessing pipeline
Scanned PDFs go through: PDF→PNG (300 DPI) → Rotate (sideways detection via row/col variance) → Deskew (angle sweep -5° to +5°) → Enhance (contrast 4.0, sharpness 2.0). This chain dramatically improves LLM accuracy on faint handwriting.

### 6. Fallback response saving
Raw LLM responses are saved to `cache/fallback/` before any post-processing. This prevents data loss if downstream steps fail. Additionally, extractors can attach `_llm_raw_text` to records — the pipeline strips it and writes a `.llm_raw.txt` file next to the output JSON, so the raw LLM output and the post-processed result are side-by-side for debugging.

### 7. File-based cache and status
Simple JSON/text files for cache and status. No database needed. Enables resume capability — if a run crashes, re-running skips completed stages.

### 8. Dual pipeline architecture
Two pipeline types coexist: `FeaturePipeline` (image-centric: prepare → chunk → LLM extract all data) and `ExcelPipeline` (schema-centric: LLM detects columns once → code extracts rows programmatically). The factory picks the right pipeline based on `FeatureConfig` vs `ExcelFeatureConfig`.

## Extension guide

### Adding a new LLM provider
1. Create `implementations/new_model.py` implementing `LanguageModel`
2. Update `factories/factory.py` to use it (config-driven)

### Adding a new preparation step
1. Create `implementations/new_step.py` implementing `PreparationStep`
2. Add it to the steps list in `factories/factory.py`

### Adding a new feature
See CLAUDE.md for the 5-file recipe.

## Reference
Architecture ported from the tamtzit_rishu project's proven patterns (LanguageModel ABC, ExcelProcessor ABC, CostLogger, retry logic).
