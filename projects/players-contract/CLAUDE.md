# Players Contract — Claude Code Instructions

## Overview

Extract financial compensation from IFA player contracts (PDF) via LLM. Uses `pdf_pipeline` shared library.

## Structure

```
src/players_contract/
  factories/   Wires pdf_pipeline implementations to features
  features/    contract_salary — IFA player contract extraction (2025/26 season)
run.py         CLI entry point
```

## Key Files

| File | Role |
|------|------|
| `factories/factory.py` | `bootstrap()` — wires all dependencies; `create_pipeline()` |
| `features/contract_salary/extractor.py` | ContractSalaryExtractor — computes yearly fields, resolves allowances |
| `features/contract_salary/prompt.py` | LLM prompt — season filter, person classification, gershayim |
| `run.py` | CLI + RTL filename recovery |

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
python run.py history [-n N]
python -m pytest tests/ -v
```

## Cache & Status

Delete both to force re-run: `rm cache, status.json -Recurse -Force`

## Adding a New Feature

Five files in `src/players_contract/features/<name>/`: `model.py`, `prompt.py`, `extractor.py`, `mapper.py`, `register.py`. Register in `factories/factory.py:bootstrap()`.
