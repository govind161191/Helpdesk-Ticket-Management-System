"""
etl/extract.py — Extract phase of the ETL pipeline.

Supports extracting ticket data from:
  - SQLite database (live source)
  - CSV files (batch import)
  - JSON files (API dump import)
"""
import csv
import json
import sqlite3
from pathlib import Path
from typing import List, Dict, Any


# ─── Database Extractor ───────────────────────────────────────────────────────

def extract_from_db(db_path: str = "./backend/helpdesk.db") -> List[Dict[str, Any]]:
    """
    Extract all ticket records directly from the SQLite database.

    Args:
        db_path: Path to the SQLite database file.

    Returns:
        List of raw ticket dictionaries.
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tickets")
    rows = [dict(row) for row in cursor.fetchall()]
    conn.close()
    print(f"[EXTRACT] Extracted {len(rows)} records from database.")
    return rows


# ─── CSV Extractor ────────────────────────────────────────────────────────────

def extract_from_csv(file_path: str) -> List[Dict[str, Any]]:
    """
    Extract ticket data from a CSV file.

    Expected columns (at minimum):
        employee_name, department, issue_category, description, priority

    Args:
        file_path: Path to the CSV input file.

    Returns:
        List of raw ticket dictionaries.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {file_path}")

    records = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            records.append(dict(row))

    print(f"[EXTRACT] Extracted {len(records)} records from CSV: {file_path}")
    return records


# ─── JSON Extractor ───────────────────────────────────────────────────────────

def extract_from_json(file_path: str) -> List[Dict[str, Any]]:
    """
    Extract ticket data from a JSON file (list of objects).

    Args:
        file_path: Path to the JSON input file.

    Returns:
        List of raw ticket dictionaries.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    with open(path, encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("JSON file must contain a top-level list of ticket objects.")

    print(f"[EXTRACT] Extracted {len(data)} records from JSON: {file_path}")
    return data
