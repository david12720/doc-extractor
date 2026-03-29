# Players Contract — Claude Code Instructions

## Project Overview

Extract financial compensation data from Israeli Football Association (IFA) player contracts (PDF) via LLM. Extracts salary, bonuses, housing/car allowances — excludes achievement-based bonuses. Uses the `pdf_pipeline` shared library.

## Structure Map

```
projects/players-contract/
├── CLAUDE.md                          # This file — project instructions
├── PLAN.md                            # Implementation plan and field mapping
├── pyproject.toml                     # Package config (depends on pdf-pipeline)
├── run.py                             # CLI entry point (run, history commands)
├── roy_example.pdf                    # Sample IFA player contract
├── src/
│   └── players_contract/
│       ├── __init__.py
│       ├── factories/
│       │   ├── __init__.py
│       │   └── factory.py             # bootstrap() — wires implementations; create_pipeline()
│       └── features/
│           ├── __init__.py
│           └── contract_salary/       # Feature: extract salary data from player contracts
│               ├── __init__.py
│               ├── model.py           # PlayerContractSalary dataclass
│               ├── prompt.py          # LLM prompt (Hebrew, season-filtered)
│               ├── extractor.py       # ContractSalaryExtractor(DataExtractor)
│               ├── mapper.py          # ContractSalaryMapper(ExcelMapper)
│               └── register.py        # register() → FeatureRegistry
└── tests/
    ├── __init__.py
    └── unit/
        ├── __init__.py
        └── test_contract_salary_extractor.py  # Mock-based unit tests
```

## Dependency Rule

```
run.py → factories/ → pdf_pipeline.implementations.*
                     → pdf_pipeline.core.*
         features/   → pdf_pipeline.abstractions.* (ONLY — never implementations)
```

## Commands

```bash
# Install (editable, for development)
pip install -e ../../libs/pdf-pipeline
pip install -e .

# Run extraction
python run.py run contract_salary <input.pdf> [-o output.json] [--ocr]

# List features
python run.py run contract_salary --list-features

# Cost history
python run.py history [-n N]

# Run tests
python -m pytest tests/ -v
```

## Registered Features

| Feature | Type | Input | Description |
|---------|------|-------|-------------|
| `contract_salary` | PDF | IFA player contracts | Salary, bonuses, housing, car for season 2025/26 |

## Key Design Decisions

- **`raw_pdf=True`**: Sends raw PDF to LLM (no image conversion) — contracts are mostly typed
- **Handwriting model**: Uses `GEMINI_MODEL_HANDWRITING` for handwritten fields (player name, ID, team)
- **Season filter**: Prompt instructs LLM to extract only 2025/26 data
- **Achievement exclusion**: Only individual performance bonuses (goals/assists/penalties) — no team-level awards
- **`points_bonus_total`**: Computed in extractor (`per_point × max_points`), not by LLM
- **Gershayim**: Prompt instructs LLM to use `״` (U+05F4) in any Hebrew abbreviated word, e.g. `בית״ר`, `בע״מ`, `ת״א`
- **Prompt examples**: Use fictional values to prevent LLM from copying them

## Cache & Status

To force a full re-run, delete both cache and status:
```powershell
rm cache, status.json -Recurse -Force
```
`status.json` is in the working directory (not inside `cache/`) and must be deleted separately.

## Adding a New Feature

Create `src/players_contract/features/<name>/` with:
1. `model.py` — dataclass for extracted fields
2. `prompt.py` — LLM prompt
3. `extractor.py` — `DataExtractor` subclass (imports from `pdf_pipeline.abstractions`)
4. `mapper.py` — `ExcelMapper` subclass
5. `register.py` — registers with `FeatureRegistry`

Then add the registration call in `factories/factory.py:bootstrap()`.
