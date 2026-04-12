# Players Contract — Architecture Decisions

For shared infrastructure decisions (preprocessing pipeline, chunk size, caching, fallback saving, dual pipeline architecture, OCR), see [`libs/pdf-pipeline/CONTEXT.md`](../../libs/pdf-pipeline/CONTEXT.md).

## 1. Raw PDF mode (`raw_pdf=True`)

IFA contracts are mostly typed text, not scanned handwriting. Sending the raw PDF directly to the LLM avoids the image conversion + preprocessing overhead and produces better results for typed documents. The handwriting model (`GEMINI_MODEL_HANDWRITING`) is still used because a subset of fields (player ID, team name) are handwritten on the IFA form.

## 2. Season filter in prompt

The contract PDF may contain salary schedules for multiple seasons (2025/26, 2026/27, 2027/28). The prompt explicitly instructs the LLM to extract only 2025/26 data. This is simpler and more reliable than post-processing multi-season output.

## 3. Computed fields vs LLM extraction

Fields that can be derived mathematically are computed in the extractor, not by the LLM:
- `*_yearly` fields = `monthly × employment_months`
- `points_bonus_total` = `points_bonus_per_point × max_points_for_bonus`

This avoids LLM arithmetic errors and keeps prompts focused on reading, not calculating.

## 4. Person type classification

Contracts cover players, coaching staff, and non-playing staff (medical, physiotherapy, etc.). The `person_type` field uses three values: `"player"`, `"coach"`, `"other"`. The `"other"` category captures all non-playing, non-coaching roles to avoid misclassification (a physiotherapist is not a coach).

## 5. Achievement bonus exclusion

The prompt explicitly excludes team-level achievement bonuses (מענקים מותנים בהשגים). Only individual performance bonuses (goals, assists, penalties) are extracted. This is a business rule, not a technical constraint.

## 6. Gershayim normalization

Hebrew abbreviated words in team names and other fields use `״` (U+05F4, Hebrew Punctuation Gershayim) not straight `"`. The prompt enforces this to produce consistent output that downstream systems can match against reference data.

## 7. RTL filename recovery

Hebrew filenames pasted from a terminal may arrive in visually-reversed character order (RTL rendering artefact). `run.py` recovers the correct filename by matching the CLI argument against files on disk using a character multiset (`Counter`) comparison — same characters, any order. This is a display artefact fix, not an encoding fix.
