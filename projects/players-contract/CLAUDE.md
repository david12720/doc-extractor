# Players Contract — Claude Code Instructions

## Overview

Extract financial compensation from IFA player contracts (PDF) via LLM. Uses `pdf_pipeline` shared library.

## Structure

```
src/players_contract/
  factories/   Wires pdf_pipeline implementations to features
  features/    contract_salary — IFA player contract extraction (2025/26 season)
  export/      JSON → Hebrew RTL Excel mappers (decoupled from pdf_pipeline)
run.py         CLI entry point
```

## Key Files

| File | Role |
|------|------|
| `factories/factory.py` | `bootstrap()` — wires all dependencies; `create_pipeline()`; `create_excel_mapper()` |
| `features/contract_salary/extractor.py` | ContractSalaryExtractor — computes yearly fields, resolves allowances |
| `features/contract_salary/prompt.py` | LLM prompt — season filter, person classification, gershayim |
| `export/excel_mapper.py` | ExcelMapper ABC (project-local; pdf_pipeline stays Excel-free) |
| `export/contract_salary_mapper.py` | Hebrew header/value translation, RTL layout, styling, number formats |
| `run.py` | CLI (`--base-dir` batch mode + RTL filename recovery) |

## Dependency Rule

```
run.py → factories/ → pdf_pipeline.implementations.*
                     → pdf_pipeline.core.*
         features/  → pdf_pipeline.abstractions.* (ONLY)
```

## Key Behaviours

- **`raw_pdf=True`**: raw PDF to LLM — contracts are mostly typed text
- **Handwriting model**: `GEMINI_MODEL_HANDWRITING` — player ID and team name are handwritten
- **Season filter**: LLM extracts only 2025/26 data
- **Person classification**: `person_type` ∈ `{"player", "coach", "other"}`; `person_role` holds the specific role
- **Computed fields**: `*_yearly` and `points_bonus_total` computed in extractor, not by LLM
- **Achievement exclusion**: individual performance bonuses only — no team-level awards
- **Gershayim**: `״` (U+05F4) in Hebrew abbreviated words
- **RTL filename recovery**: `run.py` uses `Counter` multiset matching for RTL-mangled Hebrew filenames

## Commands

```bash
pip install -e ../../libs/pdf-pipeline && pip install -e .
python run.py run contract_salary <input.pdf> [-o output.json] [--ocr]
python run.py run contract_salary -b <dir>           # batch top-level *.pdf, one LLM call per file
python run.py history [-n N]
python -m pytest tests/ -v
```

Every `run` invocation also writes an `.xlsx` next to the JSON via `create_excel_mapper`.

## Cache & Status

Delete both to force re-run: `rm cache, status.json -Recurse -Force`

## Adding a New Feature

Four files in `src/players_contract/features/<name>/`: `model.py`, `prompt.py`, `extractor.py`, `register.py`. Register in `factories/factory.py:bootstrap()`. If the feature needs Excel output, add a mapper under `src/players_contract/export/` and register it in `_EXCEL_MAPPERS` in `factories/factory.py`.
