"""
etl/load.py — Load phase of the ETL pipeline.

Supports loading transformed ticket data to:
  - SQLite database (upsert logic)
  - CSV export file (analytics / reporting)
  - JSON export file (downstream system integration)
"""
import csv
import json
import sqlite3
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any


# ─── Database Loader ──────────────────────────────────────────────────────────

def load_to_db(
    records: List[Dict[str, Any]],
    db_path: str = "./backend/helpdesk.db",
) -> int:
    """
    Upsert transformed ticket records into the SQLite database.

    - If a record has 'ticket_id', it updates the existing row.
    - Otherwise, it inserts a new row.

    Args:
        records: List of transformed ticket dicts.
        db_path: Path to SQLite DB.

    Returns:
        Number of records successfully written.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    count = 0

    for rec in records:
        if "ticket_id" in rec and rec["ticket_id"]:
            # UPDATE existing ticket
            cursor.execute(
                """
                UPDATE tickets
                SET employee_name=?, department=?, issue_category=?, description=?,
                    priority=?, status=?, resolution_notes=?
                WHERE ticket_id=?
                """,
                (
                    rec["employee_name"],
                    rec["department"],
                    rec["issue_category"],
                    rec["description"],
                    rec["priority"],
                    rec["status"],
                    rec.get("resolution_notes"),
                    rec["ticket_id"],
                ),
            )
        else:
            # INSERT new ticket
            cursor.execute(
                """
                INSERT INTO tickets
                    (employee_name, department, issue_category, description, priority, status, resolution_notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    rec["employee_name"],
                    rec["department"],
                    rec["issue_category"],
                    rec["description"],
                    rec["priority"],
                    rec.get("status", "Open"),
                    rec.get("resolution_notes"),
                ),
            )
        count += 1

    conn.commit()
    conn.close()
    print(f"[LOAD] {count} records written to database: {db_path}")
    return count


# ─── CSV Loader ───────────────────────────────────────────────────────────────

def load_to_csv(
    records: List[Dict[str, Any]],
    output_dir: str = "./database",
    filename: str = None,
) -> str:
    """
    Export transformed records to a timestamped CSV file.

    Args:
        records: Transformed ticket records (may include enriched fields).
        output_dir: Directory to write the CSV.
        filename: Override filename (auto-generated if None).

    Returns:
        Full path to the written CSV file.
    """
    if not records:
        print("[LOAD] No records to export to CSV.")
        return ""

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = Path(output_dir) / (filename or f"tickets_export_{ts}.csv")

    fieldnames = list(records[0].keys())
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(records)

    print(f"[LOAD] {len(records)} records exported to CSV: {file_path}")
    return str(file_path)


# ─── JSON Loader ──────────────────────────────────────────────────────────────

def load_to_json(
    records: List[Dict[str, Any]],
    output_dir: str = "./database",
    filename: str = None,
) -> str:
    """
    Export transformed records to a timestamped JSON file.

    Args:
        records: Transformed ticket records.
        output_dir: Directory to write the JSON.
        filename: Override filename (auto-generated if None).

    Returns:
        Full path to the written JSON file.
    """
    if not records:
        print("[LOAD] No records to export to JSON.")
        return ""

    Path(output_dir).mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_path = Path(output_dir) / (filename or f"tickets_export_{ts}.json")

    # Serialize datetime objects to strings
    def default_serializer(obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, default=default_serializer)

    print(f"[LOAD] {len(records)} records exported to JSON: {file_path}")
    return str(file_path)
