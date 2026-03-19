# Changelog

## 0.2.0 — 2026-03-20

### Added
- Attendance feature: extract employee attendance records from scanned PDFs
- Image preprocessing pipeline: PageRotator (sideways detection), PageDeskewer (skew correction), ImageEnhancer (contrast/sharpness)
- Fallback response saving in GeminiModel to prevent data loss
- Non-fatal cost logging (continues on failure)
- Debug page saving for visual inspection of preprocessed images

### Changed
- Pipeline outputs JSON instead of Excel (Excel mapping is a future step)
- Upgraded to gemini-3.1-pro-preview model
- PageRotator rewritten with variance-based sideways content detection

## 0.1.0 — 2026-03-16

### Added
- Project scaffolding with SOLID architecture
- 7 ABCs: LanguageModel, FileConverter, PreparationStep, DataExtractor, ExcelMapper, CacheManager, StatusTracker, CostLogger
- Infrastructure implementations: CsvCostLogger, FileCacheManager, JsonStatusTracker
- Preparation: PdfToImageConverter, PageRotator
- GeminiModel with retry logic and cost logging
- XlwingsMapper for Excel output via COM
- Core: FeatureRegistry, FeaturePipeline with full stage tracking and resume
- Factory for dependency wiring
- Placeholder feature to prove the architecture
- CLI entry point (run.py)
- 22 tests (unit + integration), all passing
