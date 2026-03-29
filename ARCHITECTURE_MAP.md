# ARCHITECTURE_MAP.md (AI Navigation Guide)

**Purpose:** This file provides a condensed, high-level map of the project to prevent unnecessary file exploration and token consumption. **AI Agents: Read this first before exploring subdirectories.**

---

## 1. System Topology
The project is a **Monorepo** split into a "Core Engine" (Library) and a "Domain Logic" (Application).

- **`libs/pdf-pipeline/` (The Engine):** 
  - Pure infrastructure. Handles PDF -> Image -> Preprocessing -> LLM -> JSON.
  - **Key Rule:** It knows nothing about "Payroll", "Salaries", or "Attendance". It only knows about "Fields" and "Images".
- **`projects/payroll-control/`** (The Application): 
  - Domain logic. Contains prompts, data models (Pydantic), and Excel mappings.
  - **Key Rule:** It "plugs in" to the library using the **Factory Pattern**.

---

## 2. File Structure (Condensed)
```text
Arye/
├── libs/
│   └── pdf-pipeline/             # Shared Infrastructure
│       ├── src/pdf_pipeline/
│       │   ├── abstractions/     # ABCs (Start here for understanding)
│       │   ├── core/             # Orchestration logic
│       │   ├── implementations/  # Concrete classes (Gemini, OpenCV)
│       │   └── config/           # Models, pricing, settings
│       └── tests/
├── projects/
│   └── payroll-control/          # Application Layer
│       ├── src/payroll_control/
│       │   ├── features/         # Payroll document types (plugins)
│       │   ├── factories/        # The "Brain" (Wires lib to app)
│       │   └── common/           # Domain-specific utils
│       ├── tests/
│       └── run.py                # CLI Entry Point
└── ARCHITECTURE_MAP.md           # This file
```

---

## 3. The "Contract" Layer (Abstractions)
To understand the system behavior without reading implementation code, look only at:
`libs/pdf-pipeline/src/pdf_pipeline/abstractions/`

- **`LanguageModel`**: Interface for LLM providers (Gemini, GPT).
- **`DataExtractor`**: Interface for converting LLM strings into structured objects.
- **`PreparationStep`**: Interface for image filters (Rotate, Deskew, etc.).
- **`SpreadsheetReader`**: Interface for reading Excel/CSV data.

---

## 3. Data Flow (The "Happy Path")
1. **Entry:** `projects/payroll-control/run.py` (CLI)
2. **Wiring:** `factories/factory.py` instantiates concrete classes (e.g., `GeminiModel`, `OpenCVRotation`) and passes them to the Pipeline.
3. **Execution (Scanned):** `FeaturePipeline` (in Lib) runs:
   `PDF -> PNGs -> [PreparationSteps] -> LLM -> DataExtractor -> JSON`
4. **Execution (Excel):** `ExcelPipeline` (in Lib) runs:
   `File -> SpreadsheetReader -> LLM (Schema Detection) -> Row Extraction -> JSON`

---

## 4. The "Feature" Recipe
Every document type (Attendance, Payslip, etc.) in `projects/payroll-control/src/payroll_control/features/` follows the exact same 5-file pattern. **If you have seen one, you have seen them all:**

1. `model.py`: Pydantic schema (The "What").
2. `prompt.py`: The LLM instructions (The "How").
3. `extractor.py`: Post-processing logic (The "Cleanup").
4. `mapper.py`: Column mapping for Excel (The "Translation").
5. `register.py`: Metadata for the CLI (The "Name").

---

## 5. Token-Saving Instructions for AI
- **DO NOT** read `libs/pdf-pipeline/src/pdf_pipeline/implementations/` unless debugging a specific image processing or API issue.
- **DO NOT** read more than one `feature` subfolder unless comparing logic between two document types.
- **PREFER** reading `abstractions/` over `core/` to understand "what" the system can do.
- **TRUST** the `factory.py` for understanding how the system is currently configured.
- **IGNORE** `__pycache__`, `.pytest_cache`, and `tests/` unless explicitly verifying a fix.

---

## 6. Key File Index (Fast-Track)
| File | Role |
| :--- | :--- |
| `libs/pdf-pipeline/src/pdf_pipeline/core/pipeline.py` | The main orchestration loop. |
| `projects/payroll-control/src/payroll_control/factories/factory.py` | The "Brain" where all parts are connected. |
| `projects/payroll-control/run.py` | CLI entry point and command definitions. |
