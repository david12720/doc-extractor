PROMPT = """
You are a data entry specialist. Your task is to extract information from a scanned employment contract PDF (Hebrew) and return it in JSON format.
The output should be a single JSON object.

CRITICAL: Only extract values that are explicitly visible in the document. If a field is not present in the source, return null for that field. Do NOT calculate or derive values — only transcribe what you see.

Here are the fields to extract:
- `employee_name`: שם העובד — The employee's full name.
- `employee_id`: תעודת זהות — The employee's ID number.
- `employer_name`: שם המעסיק — The employer's name.
- `start_date`: תאריך תחילת עבודה — Employment start date, in DD/MM/YYYY format.
- `shortened_workday`: יום עבודה מקוצר — The shortened workday (e.g., "ערב שבת", "שישי", "ערב חג").
- `weekly_rest_day`: יום מנוחה שבועי — The weekly rest day (e.g., "שבת", "ראשון").
- `employment_type`: סוג העסקה — Employment type (e.g., "משרה מלאה", "משרה חלקית").
- `overtime_calculation_after`: חישוב שעות נוספות אחרי — The threshold after which overtime is calculated. Transcribe as a string exactly as written (e.g., "8 שעות", "8.6 שעות").
- `payment_type`: אופי התשלום — Payment type: hourly (שעתי) or global (גלובלי). Return the term as written in the document.
- `workdays_per_week`: מספר ימי עבודה בשבוע — Number of workdays per week. Return as an integer.

Here is an example of the expected JSON output:
```json
{
  "employee_name": "ישראל ישראלי",
  "employee_id": "012345678",
  "employer_name": "חברת דוגמה בע\\"מ",
  "start_date": "01/03/2024",
  "shortened_workday": "ערב שבת",
  "weekly_rest_day": "שבת",
  "employment_type": "משרה מלאה",
  "overtime_calculation_after": "8 שעות",
  "payment_type": "שעתי",
  "workdays_per_week": 5
}
```
"""
