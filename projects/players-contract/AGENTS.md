# Players Contract — Agent Configuration

## Agents

### feature-dev
Handles the `contract_salary` feature. Imports only from `pdf_pipeline.abstractions`.

**Owns:** `src/players_contract/features/`
**Tests:** `tests/unit/test_contract_salary_extractor.py`

### factory-wiring
Handles the factory layer, the CLI entry point, and the project-local Excel export module (which is wired through the factory).

**Owns:** `src/players_contract/factories/`, `src/players_contract/export/`, `run.py`
**Tests:** `tests/unit/test_contract_salary_mapper.py`
