# Workspace Root

**Do not work from here** — navigate to the relevant sub-project. Each has its own `CLAUDE.md`.

## Structure

```
libs/pdf-pipeline/          # Shared pipeline library (package: pdf_pipeline)
  src/pdf_pipeline/
    abstractions/           # ABCs — all swappable contracts
    core/                   # Pipeline orchestration (FeaturePipeline, ExcelPipeline)
    implementations/        # Concrete classes (Gemini, image processing, OCR, ...)
    config/                 # Settings and pricing
projects/payroll-control/   # Payroll app (consumes pdf_pipeline)
  src/payroll_control/
    factories/              # Wires implementations to features
    features/               # attendance, payslip, pension, employment_contract, ...
projects/players-contract/  # IFA player contract salary extraction (consumes pdf_pipeline)
  src/players_contract/
    factories/
    features/               # contract_salary
```

## Key Files

| File | Role |
|------|------|
| `libs/pdf-pipeline/src/pdf_pipeline/abstractions/` | All ABCs — start here to understand the system |
| `libs/pdf-pipeline/src/pdf_pipeline/core/pipeline.py` | Main orchestration loop |
| `projects/payroll-control/src/payroll_control/factories/factory.py` | Wires payroll-control together |
| `projects/players-contract/src/players_contract/factories/factory.py` | Wires players-contract together |

## Navigation Rules

- **PREFER** `abstractions/` over `core/` to understand what the system can do
- **TRUST** `factory.py` for how the system is currently configured
- **SKIP** `implementations/` unless debugging a specific API or image-processing issue
- **SKIP** `__pycache__`, `.pytest_cache`, `tests/` unless verifying a fix
