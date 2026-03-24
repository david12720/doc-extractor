# PaytollControl — Claude Code Instructions

## Project Overview

Payroll control tool: extract data from scanned documents (PDF/PNG) via LLM, structure it, and output as JSON. Built with a generic pipeline — new document types ("features") are added without changing existing code.

## Architecture

- **abstractions/**: 7 ABCs defining all contracts
- **core/**: Business logic (FeaturePipeline, ExcelPipeline, FeatureRegistry) — imports only from abstractions/
- **implementations/**: Concrete classes (Gemini, image processing, file cache, etc.)
- **features/<name>/**: Self-contained feature subpackages (prompt, model, extractor, mapper, register)
- **factories/**: Wires everything together
- **config/**: Settings and pricing constants

## Dependency Rule

```
run.py → factories/ → implementations/ → abstractions/
                     → core/ → abstractions/
         features/ → abstractions/ (+ core/feature_registry)
```

**core/ and features/ NEVER import from implementations/**

## Image Preparation Pipeline

PDF pages go through this pipeline before LLM extraction:

1. **PdfToImageConverter** — renders each PDF page to PNG at 300 DPI
2. **PageRotator** — detects and corrects rotation (landscape pages, sideways content in portrait pages)
3. **PageDeskewer** — corrects small skew angles from diagonal scanning
4. **ImageEnhancer** — increases contrast and sharpness for faint handwriting

## Adding a New Feature

Create `src/payroll_control/features/<name>/` with:
1. `prompt.py` — LLM prompt
2. `model.py` — dataclass for extracted fields
3. `extractor.py` — DataExtractor subclass (depends on abstractions only)
4. `mapper.py` — ExcelMapper subclass (depends on abstractions only)
5. `register.py` — registers with FeatureRegistry

Then add the registration call in `factories/factory.py:bootstrap()`.

## Library-Extractable Core (Constraint)

The core PDF-to-JSON pipeline (preprocessing, chunking, LLM calls, caching, fallback saving) is designed to be extractable as a standalone library in the future. **All new code must preserve this boundary.**

### What belongs to the core pipeline (future library)
- Image preprocessing: PdfToImageConverter, PageRotator, PageDeskewer, ImageEnhancer
- LLM client: GeminiModel (and any future providers)
- Chunking logic, retry logic, cost logging
- Abstractions: LanguageModel, FileConverter, PreparationStep, CostLogger, CacheManager
- Core pipeline orchestration: FeaturePipeline

### What belongs to the consuming application (NOT the library)
- Feature-specific code: prompts, data models, extractors, mappers
- CLI (run.py)
- FeatureRegistry, factory wiring
- Excel/output formatting
- Application-level config (which feature to run, file paths)

### Rules for new code
1. **Core pipeline code must never import from features/** — no prompt, model, or extractor references
2. **Core pipeline code must never depend on a specific data schema** — it receives a prompt and returns raw LLM text; parsing is the consumer's job
3. **New preprocessing steps** go behind the PreparationStep ABC — no inline image processing in pipeline or feature code
4. **New LLM providers** go behind the LanguageModel ABC — feature code never references a specific SDK
5. **No application-level concerns in core** — CLI args, output path decisions, feature registration stay outside
6. **If you're unsure whether code belongs in core or application** — keep it in the application side; it's easier to move into the library later than to extract it out

## Commands

- Run tests: `python -m pytest tests/ -v`
- CLI help: `python run.py --help`
- Run a feature: `python run.py run <feature_name> <input_files...> [-o output.json]`
- Cost history: `python run.py history [-n N]`

## Registered Features

| Feature | Type | Input | Description |
|---------|------|-------|-------------|
| `attendance` | PDF | Scanned attendance sheets | Extracts daily entry/exit times per employee |
| `payslip` | PDF | Scanned payslips | Extracts hours breakdown, wages, gross/net salary |
| `excel_attendance` | Excel | Attendance workbooks | LLM-detected schema, extracts times + person ID |

## Cache & Status Keys

Cache and status entries are keyed per input file(s), not per feature name:
- Single file: `{feature}_{file_stem}` (e.g. `payslip_תלושי שכר`)
- Multiple files: `{feature}_{hash}` (deterministic hash of sorted stems)

Default output paths also include the file stem: `output/{feature}_{file_stem}.json`

## Conventions

- All dependencies are injected — never instantiate concrete classes in business logic
- Tests use mocks/fakes — no real API calls
- Config constants live in `config/settings.py` and `config/pricing.py`
- Pipeline outputs JSON; Excel mapping is a future separate step
- Raw LLM responses are saved to `cache/fallback/` before any post-processing
- Cost logging is non-fatal — failures are warned but don't crash the pipeline
- Single cost log file (`api_cost_log.csv`) shared across all features and pipelines
