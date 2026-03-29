# pdf-pipeline — Agent Configuration

## Agents

### pipeline-core
Handles changes to `core/` and `abstractions/`. Understands the pipeline orchestration, feature registry, and ABC contracts. Must ensure dependency rule: core/ imports only from abstractions/.

**Owns:** `src/pdf_pipeline/abstractions/`, `src/pdf_pipeline/core/`, `src/pdf_pipeline/config/`
**Tests:** `tests/unit/test_feature_registry.py`, `tests/unit/test_excel_pipeline.py`, `tests/unit/test_preparation_pipeline.py`

### implementations
Handles changes to concrete implementations. Each implementation must satisfy its ABC contract. Must ensure implementations/ imports only from abstractions/ and config/, never from core/.

**Owns:** `src/pdf_pipeline/implementations/`
**Tests:** `tests/unit/test_csv_cost_logger.py`, `tests/unit/test_file_cache_manager.py`, `tests/unit/test_json_status_tracker.py`, `tests/unit/test_llm_schema_detector.py`
