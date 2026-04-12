# doc-extractor — Document Data Extraction

Extract structured data from scanned documents (PDF/PNG) and Excel files using LLMs, output structured JSON.

## Structure

| Path | Description |
|------|-------------|
| [`libs/pdf-pipeline/`](libs/pdf-pipeline/README.md) | Generic PDF-to-JSON pipeline (shared library). Domain-agnostic — rendering, preprocessing, LLM, caching. |
| [`projects/payroll-control/`](projects/payroll-control/README.md) | Payroll documents: attendance, payslips, pension, employment contracts. |
| [`projects/players-contract/`](projects/players-contract/README.md) | IFA player contract salary extraction. |

## Quick Start

```bash
pip install -e libs/pdf-pipeline
pip install -e projects/payroll-control
pip install -e projects/players-contract
export GEMINI_API_KEY=your_key_here
```

See each project's README for usage and features. For pipeline internals, see [`libs/pdf-pipeline/README.md`](libs/pdf-pipeline/README.md).
