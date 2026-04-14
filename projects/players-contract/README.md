# Players Contract

Extract financial compensation data from Israeli Football Association (IFA) player contracts (PDF) via LLM, output structured JSON and a Hebrew right-to-left Excel report.

## Setup

```bash
pip install -e ../../libs/pdf-pipeline
pip install -e .
export GEMINI_API_KEY=your_key_here
```

## Usage

```bash
# Single contract (or several explicit files merged into one LLM call)
python run.py run contract_salary player_contract.pdf -o result.json

# Batch: every top-level *.pdf in a directory, one LLM call per file,
# aggregated into <base_dir>/<base_dir>.json + <base_dir>/<base_dir>.xlsx
python run.py run contract_salary -b path/to/contracts_dir

python run.py run contract_salary player_contract.pdf --ocr  # Cloud Vision OCR for better handwriting
python run.py history [-n N]  # show API cost history
```

Every `run` invocation also writes a styled, RTL Hebrew `.xlsx` next to the JSON output.

## Features

| Feature | Type | Input | Description |
|---------|------|-------|-------------|
| `contract_salary` | PDF | IFA player contracts | Salary, allowances, bonuses for season 2025/26 |

### Extracted fields

| Field | Source |
|-------|--------|
| `player_id`, `team_name`, `season` | IFA form (handwritten) |
| `person_type` | `"player"`, `"coach"`, or `"other"` (medical/support staff) |
| `person_role` | Specific role, returned verbatim in Hebrew (e.g., `"פיזיותרפיסט"`, `"עוזר מאמן"`) |
| `employment_months` | Contract duration |
| `base_salary_monthly` / `_yearly` | Salary section (yearly = monthly × months) |
| `housing_allowance_monthly` / `_yearly` | Salary section (yearly computed) |
| `car_allowance_monthly` / `_yearly` | Salary/bonus section (yearly computed) |
| `points_bonus_per_point`, `max_points_for_bonus` | Bonus section |
| `points_bonus_total` | Computed (`per_point × max_points`) |
| `goal_assist_penalty_bonus` | Individual performance bonuses only |

## Tests

```bash
python -m pytest tests/ -v
```

## Architecture

See [CONTEXT.md](CONTEXT.md) for design decisions and [CLAUDE.md](CLAUDE.md) for development instructions.
