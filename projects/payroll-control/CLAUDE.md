# Payroll Control — Claude Code Instructions

## Overview

Payroll document processing: extracts attendance, payslips, pension, and employment contract data from scanned PDFs and Excel files via LLM.

## Structure

```
src/payroll_control/
  factories/   Wires pdf_pipeline implementations to features (only place with concrete imports)
  features/    One subpackage per document type — attendance, payslip, pension, employment_contract, excel_attendance, placeholder
run.py         CLI entry point
```

## Key Files

| File | Role |
|------|------|
| `factories/factory.py` | `bootstrap()` — wires all dependencies; `create_pipeline()` |
| `features/<name>/extractor.py` | DataExtractor subclass — LLM response → typed records |
| `features/<name>/prompt.py` | LLM prompt for this feature |
| `run.py` | CLI: `run <feature> <files>`, `history` |

## Dependency Rule

```
run.py → factories/ → pdf_pipeline.implementations.*
                     → pdf_pipeline.core.*
         features/  → pdf_pipeline.abstractions.* (ONLY)
```

## Adding a New Feature

Create `src/payroll_control/features/<name>/` with:
1. `prompt.py` — LLM prompt
2. `model.py` — dataclass for extracted fields
3. `extractor.py` — DataExtractor subclass
4. `mapper.py` — ExcelMapper subclass
5. `register.py` — registers with FeatureRegistry

Then add the registration call in `factories/factory.py:bootstrap()`.

## Commands

- Run tests: `python -m pytest tests/ -v`
- Run a feature: `python run.py run <feature_name> <input_files...> [-o output.json]`
- Cost history: `python run.py history [-n N]`

## Feature Notes

- `employment_contract`: always uses Cloud Vision OCR (constructed unconditionally in `factory.py`). Prompt extracts `start_date` from the **top header area** of the form; `shortened_workday` accepts `"על פי הדין"`; `payment_type` includes `"חודשי"` alongside `"שעתי"` and `"גלובלי"`.

## Cache & Status Keys

Keyed per input file(s):
- Single file: `{feature}_{file_stem}` (e.g. `payslip_תלושי שכר`)
- Multiple files: `{feature}_{hash}` (deterministic hash of sorted stems)

## Conventions

- All dependencies are injected — never instantiate concrete classes in business logic
- Tests use mocks/fakes — no real API calls
- Raw LLM responses saved to `cache/fallback/` before any post-processing
- If an extractor attaches `_llm_raw_text` to a record, the pipeline strips it and saves it as a `.llm_raw.txt` file
- Cost logging is non-fatal — failures are warned but don't crash
