# Workspace Root

This is a monorepo workspace. **Do not work from here** — navigate to the relevant sub-project:

- **`libs/pdf-pipeline/`** — Generic PDF-to-JSON extraction pipeline via LLM (shared library)
- **`projects/payroll-control/`** — Payroll document processing application (consumes pdf-pipeline)

Each sub-project has its own `CLAUDE.md` with architecture details, commands, and conventions.

## Workspace Structure

```
Arye/
├── libs/
│   └── pdf-pipeline/          # Shared library (package: pdf_pipeline)
│       ├── src/pdf_pipeline/
│       │   ├── abstractions/  # ABCs (LanguageModel, DataExtractor, ...)
│       │   ├── core/          # Pipeline orchestration (FeaturePipeline, ExcelPipeline)
│       │   ├── config/        # Settings, pricing
│       │   └── implementations/ # Concrete classes (Gemini, image processing, ...)
│       └── tests/
├── projects/
│   └── payroll-control/       # Payroll app (consumes pdf_pipeline)
│       ├── src/payroll_control/
│       │   ├── factories/     # Wires implementations to features
│       │   └── features/      # Domain features (attendance, payslip, pension, ...)
│       ├── tests/
│       └── run.py             # CLI entry point
└── CLAUDE.md                  # This file
```

## Quick Start

```bash
# Install both packages (editable, for development)
pip install -e libs/pdf-pipeline
pip install -e projects/payroll-control

# Run library tests
cd libs/pdf-pipeline && python -m pytest tests/ -v

# Run app tests
cd projects/payroll-control && python -m pytest tests/ -v
```
