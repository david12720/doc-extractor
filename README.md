# PaytollControl

Extract payroll data from scanned documents (PDF/PNG) via LLM, output structured JSON.

## Setup

```bash
pip install -r requirements.txt
export GEMINI_API_KEY=your_key_here
```

## Usage

```bash
python run.py run <feature> <input_files...> [-o output.json] [-w work_dir]
python run.py run --list-features dummy  # list available features
python run.py run attendance scanned_doc.pdf -o result.json
python run.py run payslip payslip.pdf -o result.json
python run.py run pension pension_report.pdf -o result.json
python run.py run excel_attendance file1.xlsx file2.xlsx -o result.json
python run.py history [-n N]  # show API cost history
```

## Tests

```bash
python -m pytest tests/ -v
```

## Architecture

See [CONTEXT.md](CONTEXT.md) for architecture decisions and [CLAUDE.md](CLAUDE.md) for development instructions.

## Adding a new feature

Create `src/payroll_control/features/<name>/` with 5 files:
1. `prompt.py` — LLM prompt
2. `model.py` — dataclass for fields
3. `extractor.py` — DataExtractor subclass
4. `mapper.py` — ExcelMapper subclass
5. `register.py` — register with FeatureRegistry

Then add the registration call in `factories/factory.py`.
