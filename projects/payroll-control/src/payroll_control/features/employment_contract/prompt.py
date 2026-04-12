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
- `start_date`: תאריך תחילת עבודה — Employment start date in DD/MM/YYYY format. This date is typically handwritten at the TOP of the form, in the header area near the employee name and ID — NOT in the main table. Look for a date field labeled "תאריך תחילת עבודה" or "תחילת עבודה" in the top section of the document. IGNORE all other dates: signature dates at the bottom, notice dates ("תאריך ההודעה"), document print dates, and dates in the stamp/seal.{start_date_hint}
- `start_date_confidence`: מידת הוודאות — An integer from 0 to 100 representing your confidence in the start_date value. 100 = clearly legible, 0 = completely unreadable. If a hint was provided, indicate how well the hint matches what you see in the document.
- `shortened_workday`: יום עבודה מקוצר — The shortened workday. Common values: "ערב שבת", "שישי", "ערב חג". This field is often filled with "על פי הדין" — if you see that phrase (handwritten, stamped, or as a checkmark next to the option), return "על פי הדין". Do NOT return null if "על פי הדין" is written in the cell.
- `weekly_rest_day`: יום מנוחה שבועי — The weekly rest day (e.g., "שבת", "ראשון").
- `employment_type`: סוג העסקה — Employment type (e.g., "משרה מלאה", "משרה חלקית").
- `overtime_calculation_after`: חישוב שעות נוספות אחרי — The threshold after which overtime is calculated. Transcribe as a string exactly as written (e.g., "8 שעות", "8.6 שעות").
- `payment_type`: אופי התשלום — Payment type. Possible values: "שעתי" (hourly), "חודשי" (monthly), or "גלובלי" (global/salaried). The contract form typically lists these as options where one is circled, underlined, or marked. If both options appear marked and you cannot determine which one is the intended choice, return both separated by a slash (e.g., "שעתי/חודשי").
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

START_DATE_HINT = " הערה: על פי מקור מהימן (תלוש שכר), תאריך תחילת העבודה של העובד הוא {expected_date}. השתמש בתאריך הזה כברירת מחדל. שנה אותו רק אם אתה רואה בבירור מוחלט תאריך שונה בשדה 'תאריך תחילת עבודה' בטבלה הראשית — לא בחותמת, לא בתאריך חתימה, ולא בתאריך הודעה. אם יש ספק כלשהו, העדף את התאריך מהרמז."
NO_HINT = ""

OCR_SECTION = """

IMPORTANT — OCR Reference Text:
A dedicated OCR engine has independently scanned this document. The OCR text below is highly accurate for reading handwritten and printed characters. When you encounter hard-to-read handwritten values (especially dates and numbers), prefer the OCR reading over your own visual interpretation.

{ocr_text}

Use this OCR text as the authoritative source for handwritten values. If the OCR text and your visual reading disagree, trust the OCR text.
"""


def build_prompt(
    expected_start_date: str | None = None,
    ocr_texts: list[str] | None = None,
) -> str:
    if expected_start_date:
        hint = START_DATE_HINT.replace("{expected_date}", expected_start_date)
    else:
        hint = NO_HINT
    result = PROMPT.replace("{start_date_hint}", hint)

    if ocr_texts:
        ocr_combined = "\n--- Page Break ---\n".join(
            f"Page {i + 1}:\n{text}" for i, text in enumerate(ocr_texts) if text
        )
        result += OCR_SECTION.replace("{ocr_text}", ocr_combined)

    return result
