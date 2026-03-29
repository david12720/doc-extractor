# PaytollControl — Claude Code Instructions

## Project Overview

Payroll control tool: extract data from scanned documents (PDF/PNG) via LLM, structure it, and output as JSON. Uses the `pdf_pipeline` shared library for the core extraction pipeline.

## File Architecture

```
src/payroll_control/
├── __init__.py
├── factories/
│   ├── __init__.py
│   └── factory.py              # bootstrap() — wires pdf_pipeline implementations to features
└── features/
    ├── __init__.py
    ├── attendance/
    │   ├── extractor.py        # AttendanceExtractor (DataExtractor)
    │   ├── mapper.py           # AttendanceMapper (ExcelMapper)
    │   ├── model.py            # AttendanceRecord dataclass
    │   ├── prompt.py           # LLM prompt
    │   └── register.py         # register_attendance()
    ├── employment_contract/
    │   ├── extractor.py        # EmploymentContractExtractor (DataExtractor)
    │   ├── mapper.py           # EmploymentContractMapper (ExcelMapper)
    │   ├── prompt.py           # LLM prompt
    │   └── register.py         # register_employment_contract()
    ├── excel_attendance/
    │   ├── model.py            # ExcelAttendanceRecord dataclass
    │   ├── prompt.py           # Schema detection prompt
    │   ├── record_builder.py   # Builds records from detected schema
    │   └── register.py         # register_excel_attendance()
    ├── payslip/
    │   ├── extractor.py        # PayslipExtractor (DataExtractor)
    │   ├── mapper.py           # PayslipMapper (ExcelMapper)
    │   ├── model.py            # PayslipRecord dataclass
    │   ├── prompt.py           # LLM prompt
    │   └── register.py         # register_payslip()
    ├── pension/
    │   ├── extractor.py        # PensionExtractor (DataExtractor)
    │   ├── mapper.py           # PensionMapper (ExcelMapper)
    │   ├── prompt.py           # LLM prompt
    │   └── register.py         # register_pension()
    └── placeholder/
        ├── extractor.py        # PlaceholderExtractor (DataExtractor)
        ├── mapper.py           # PlaceholderMapper (ExcelMapper)
        ├── model.py            # PlaceholderRecord dataclass
        ├── prompt.py           # LLM prompt
        └── register.py         # register_placeholder()

run.py                          # CLI entry point
conftest.py                     # Shared test fixtures

tests/
├── fixtures/                   # Test PNG images
├── integration/
│   └── test_pipeline_integration.py
└── unit/
    ├── test_architecture_boundary.py
    ├── test_attendance_extractor.py
    ├── test_attendance_mapper.py
    ├── test_employment_contract_extractor.py
    ├── test_excel_attendance_record_builder.py
    ├── test_payslip_extractor.py
    ├── test_payslip_mapper.py
    ├── test_pension_extractor.py
    └── test_placeholder_extractor.py
```

The core pipeline (abstractions, implementations, config, orchestration) lives in `libs/pdf-pipeline/`. This project imports from `pdf_pipeline.*`.

## Dependency Rule

```
run.py → factories/ → pdf_pipeline.implementations.*
                     → pdf_pipeline.core.*
         features/ → pdf_pipeline.abstractions.* (only abstractions, never implementations)
```

**Features NEVER import from pdf_pipeline.implementations — only abstractions.**

## Adding a New Feature

Create `src/payroll_control/features/<name>/` with:
1. `prompt.py` — LLM prompt
2. `model.py` — dataclass for extracted fields
3. `extractor.py` — DataExtractor subclass (imports from `pdf_pipeline.abstractions`)
4. `mapper.py` — ExcelMapper subclass (imports from `pdf_pipeline.abstractions`)
5. `register.py` — registers with FeatureRegistry

Then add the registration call in `factories/factory.py:bootstrap()`.

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
| `pension` | PDF | Pension deposit reports | Extracts deposit history per insured person |
| `employment_contract` | PDF | Scanned employment contracts | Extracts contract terms: work schedule, payment type, overtime |
| `excel_attendance` | Excel | Attendance workbooks | LLM-detected schema, extracts times + person ID |

## Cache & Status Keys

Cache and status entries are keyed per input file(s), not per feature name:
- Single file: `{feature}_{file_stem}` (e.g. `payslip_תלושי שכר`)
- Multiple files: `{feature}_{hash}` (deterministic hash of sorted stems)

Default output paths also include the file stem: `output/{feature}_{file_stem}.json`

## Conventions

- All dependencies are injected — never instantiate concrete classes in business logic
- Tests use mocks/fakes — no real API calls
- Pipeline outputs JSON; Excel mapping is a future separate step
- Raw LLM responses are saved to `cache/fallback/` before any post-processing
- If an extractor attaches `_llm_raw_text` to a record, the pipeline strips it and saves it as a separate `.llm_raw.txt` file next to the output JSON
- Cost logging is non-fatal — failures are warned but don't crash the pipeline
- Single cost log file (`api_cost_log.csv`) shared across all features and pipelines
