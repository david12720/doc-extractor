PROMPT = """
You are a data entry specialist. Your task is to extract information from a scanned employment contract PDF (Hebrew) and return it in JSON format.
The output should be a single JSON object.

CRITICAL: Only extract values that are explicitly visible in the document. If a field is not present in the source, return null for that field. Do NOT calculate or derive values — only transcribe what you see.

IMPORTANT — "על פי הדין" (according to law): Many fields in employment contracts are filled with "על פי הדין" or "עפ"י הדין" instead of a specific value. When you see this phrase (or any variation of it) as the value for a field, return the string "על פי הדין" exactly. Do not try to interpret, guess, or look up what the law says — just return the literal phrase.

IMPORTANT — Employer name: The employer name often appears in a stamp/seal (חותמת) at the bottom of the document, which is the most reliable source. Prefer reading the employer name from the stamp over the handwritten/printed text in the body of the contract.

Here are the fields to extract:
- `employee_name`: שם העובד — The employee's full name.
- `employee_id`: תעודת זהות — The employee's ID number.
- `employer_name`: שם המעסיק — The employer's name. Look for the company stamp at the bottom of the document as the primary source.
- `start_date`: תאריך תחילת עבודה — Employment start date in DD/MM/YYYY format. This field appears in the main table of the contract, in the row labeled "תאריך תחילת עבודה" or "תחילת עבודה". Do NOT confuse it with the signature date or the notice date ("תאריך ההודעה") at the bottom of the document.{start_date_hint}
- `start_date_confidence`: מידת הוודאות — An integer from 0 to 100 representing your confidence in the start_date value. 100 = clearly legible, 0 = completely unreadable. If a hint was provided, indicate how well the hint matches what you see in the document.
- `shortened_workday`: יום עבודה מקוצר — The shortened workday (e.g., "ערב שבת", "שישי", "ערב חג").
- `weekly_rest_day`: יום מנוחה שבועי — The weekly rest day (e.g., "שבת", "ראשון").
- `employment_type`: סוג העסקה — Employment type (e.g., "משרה מלאה", "משרה חלקית").
- `overtime_calculation_after`: חישוב שעות נוספות אחרי — The threshold after which overtime is calculated. Transcribe as a string exactly as written (e.g., "8 שעות", "8.6 שעות").
- `payment_type`: אופי התשלום — Payment type: hourly (שעתי) or global (גלובלי). Return the term as written in the document.
- `workdays_per_week`: מספר ימי עבודה בשבוע — Number of workdays per week. Return as an integer.
- `wage_rate`: תעריף שכר — The wage rate as a number (e.g., 35.50). This is the base rate the employee is paid. Extract the numeric value from the salary table in the contract.
- `wage_rate_type`: סוג תעריף — The unit of the wage rate. Must be one of: "שעתי" (hourly), "יומי" (daily), "חודשי" (monthly). Determine from the contract which type applies based on the payment structure described (e.g., if the contract specifies an hourly rate, return "שעתי").

Here is an example of the expected JSON output:
```json
{
  "employee_name": "ישראל ישראלי",
  "employee_id": "012345678",
  "employer_name": "חברת דוגמה בע\\"מ",
  "start_date": "01/03/2024",
  "start_date_confidence": 85,
  "shortened_workday": "ערב שבת",
  "weekly_rest_day": "שבת",
  "employment_type": "משרה מלאה",
  "overtime_calculation_after": "8 שעות",
  "payment_type": "שעתי",
  "workdays_per_week": 5,
  "wage_rate": 35.50,
  "wage_rate_type": "שעתי"
}
```
"""

START_DATE_HINT = " הערה: על פי מקור חיצוני (תלוש שכר), תאריך תחילת העבודה הצפוי הוא {expected_date}. אמת מול מה שכתוב במסמך — אם מה שאתה רואה תואם, השתמש בתאריך הזה. אם אתה רואה בבירור תאריך אחר, החזר את מה שאתה רואה."
NO_HINT = ""


def build_prompt(expected_start_date: str | None = None) -> str:
    if expected_start_date:
        hint = START_DATE_HINT.replace("{expected_date}", expected_start_date)
    else:
        hint = NO_HINT
    return PROMPT.replace("{start_date_hint}", hint)
