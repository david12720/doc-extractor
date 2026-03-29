# PaytollControl — Agent Configuration

## Agents

### feature-dev
Handles changes to feature subpackages in `src/payroll_control/features/`. Each feature follows the 5-file pattern (prompt, model, extractor, mapper, register). Features import only from `pdf_pipeline.abstractions`, never from `pdf_pipeline.implementations`.

**Owns:** `src/payroll_control/features/`
**Tests:** `tests/unit/test_attendance_*.py`, `tests/unit/test_payslip_*.py`, `tests/unit/test_pension_*.py`, `tests/unit/test_employment_contract_*.py`, `tests/unit/test_excel_attendance_*.py`, `tests/unit/test_placeholder_*.py`

### factory-wiring
Handles the factory layer that wires `pdf_pipeline` implementations to feature configs. Only place in this project that imports concrete classes.

**Owns:** `src/payroll_control/factories/`, `run.py`
**Tests:** `tests/unit/test_architecture_boundary.py`, `tests/integration/test_pipeline_integration.py`
