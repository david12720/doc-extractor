# Arye — Document Data Extraction

Extract structured data from scanned documents (PDF/PNG) and Excel files using LLMs, output structured JSON.

## Structure

| Path | Description |
|------|-------------|
| `libs/pdf-pipeline/` | Generic PDF-to-JSON pipeline (shared library). Domain-agnostic — rendering, preprocessing, LLM, caching. |
| `projects/payroll-control/` | Payroll documents: attendance, payslips, pension, employment contracts. |
| `projects/players-contract/` | IFA player contract salary extraction. |

## Quick Start

```bash
pip install -e libs/pdf-pipeline
pip install -e projects/payroll-control
pip install -e projects/players-contract
export GEMINI_API_KEY=your_key_here
```

See each project's `README.md` for usage and features.
