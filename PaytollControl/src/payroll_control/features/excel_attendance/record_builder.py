from datetime import datetime, time

from ...abstractions.schema_detector import ColumnMapping

COLUMN_LETTER_TO_INDEX = {chr(c): c - ord("A") for c in range(ord("A"), ord("Z") + 1)}


def _col_index(letter: str) -> int:
    return COLUMN_LETTER_TO_INDEX[letter.upper()]


def _format_date(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.strftime("%d/%m/%Y")
    text = str(value).strip()
    if not text:
        return None
    return text


def _format_time(value) -> str | None:
    if value is None:
        return None
    if isinstance(value, time):
        return value.strftime("%H:%M")
    if isinstance(value, datetime):
        return value.strftime("%H:%M")
    text = str(value).strip()
    if not text:
        return None
    return text


def build_records(rows: list[list], mapping: ColumnMapping, sheet: str) -> list[dict]:
    pid_idx = _col_index(mapping.person_id_column)
    date_idx = _col_index(mapping.date_column)
    from_idx = _col_index(mapping.from_time_column)
    to_idx = _col_index(mapping.to_time_column)

    records: list[dict] = []
    for row in rows:
        if len(row) <= max(pid_idx, date_idx, from_idx, to_idx):
            continue

        person_id = _format_person_id(row[pid_idx])
        date_val = _format_date(row[date_idx])
        from_val = _format_time(row[from_idx])
        to_val = _format_time(row[to_idx])

        if not person_id or not date_val or not from_val or not to_val:
            continue

        records.append({
            "person_id": person_id,
            "date": date_val,
            "from_time": from_val,
            "to_time": to_val,
            "sheet": sheet,
        })

    return records


def _format_person_id(value) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        return None
    return text
