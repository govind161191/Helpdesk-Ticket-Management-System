"""
etl/etl_pipeline.py — ETL Pipeline Orchestrator

Coordinates the Extract → Transform → Load workflow for the
Helpdesk Ticket Management System.

Usage examples:
    # Run full pipeline from DB → CSV export
    python -m etl.etl_pipeline --source db --target csv

    # Import tickets from a CSV file into the DB
    python -m etl.etl_pipeline --source csv --input data/tickets_raw.csv --target db

    # Dry run (extract + transform only, no load)
    python -m etl.etl_pipeline --source db --dry-run
"""
import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# Allow running as a module from project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from etl.extract import extract_from_db, extract_from_csv, extract_from_json
from etl.transform import transform
from etl.load import load_to_db, load_to_csv, load_to_json


# ─── Pipeline Run Log ─────────────────────────────────────────────────────────

class PipelineLog:
    def __init__(self):
        self.start_time = datetime.now()
        self.stages: list = []

    def log_stage(self, stage: str, detail: str):
        ts = datetime.now().strftime("%H:%M:%S")
        entry = f"[{ts}] [{stage}] {detail}"
        self.stages.append(entry)
        print(entry)

    def summary(self) -> dict:
        elapsed = (datetime.now() - self.start_time).total_seconds()
        return {
            "started_at": self.start_time.isoformat(),
            "elapsed_seconds": round(elapsed, 2),
            "stages": self.stages,
        }


# ─── Pipeline Entry Point ─────────────────────────────────────────────────────

def run_pipeline(
    source: str = "db",
    target: str = "csv",
    input_path: str = None,
    db_path: str = "./backend/helpdesk.db",
    output_dir: str = "./database",
    dry_run: bool = False,
) -> dict:
    """
    Execute the full ETL pipeline.

    Args:
        source:     Data source — 'db', 'csv', or 'json'
        target:     Data target — 'db', 'csv', 'json', or 'all'
        input_path: Path to input file (required for csv/json source)
        db_path:    SQLite DB path
        output_dir: Directory for exported files
        dry_run:    If True, skip the load phase

    Returns:
        Summary dict with pipeline run metadata.
    """
    log = PipelineLog()
    result = {}

    # ── EXTRACT ───────────────────────────────────────────────────────────────
    log.log_stage("EXTRACT", f"Source='{source}' | Input='{input_path or db_path}'")
    try:
        if source == "db":
            raw_records = extract_from_db(db_path)
        elif source == "csv":
            if not input_path:
                raise ValueError("--input is required when source=csv")
            raw_records = extract_from_csv(input_path)
        elif source == "json":
            if not input_path:
                raise ValueError("--input is required when source=json")
            raw_records = extract_from_json(input_path)
        else:
            raise ValueError(f"Unknown source: '{source}'. Choose from: db, csv, json")
        log.log_stage("EXTRACT", f"Extracted {len(raw_records)} raw records.")
        result["extracted"] = len(raw_records)
    except Exception as e:
        log.log_stage("EXTRACT", f"FAILED — {e}")
        result["error"] = str(e)
        result["summary"] = log.summary()
        return result

    # ── TRANSFORM ─────────────────────────────────────────────────────────────
    log.log_stage("TRANSFORM", "Starting data validation, normalization, and enrichment...")
    valid_records, rejected_records = transform(raw_records)
    result["valid"] = len(valid_records)
    result["rejected"] = len(rejected_records)
    log.log_stage(
        "TRANSFORM",
        f"Valid: {len(valid_records)} | Rejected: {len(rejected_records)}"
    )

    # Save rejected records for review
    if rejected_records:
        reject_path = Path(output_dir) / "rejected_tickets.json"
        reject_path.parent.mkdir(parents=True, exist_ok=True)
        with open(reject_path, "w") as f:
            json.dump(rejected_records, f, indent=2, default=str)
        log.log_stage("TRANSFORM", f"Rejected records saved to: {reject_path}")

    # ── LOAD ──────────────────────────────────────────────────────────────────
    if dry_run:
        log.log_stage("LOAD", "DRY RUN — skipping load phase.")
        result["loaded"] = 0
    else:
        log.log_stage("LOAD", f"Target='{target}'")
        try:
            if target in ("db", "all"):
                count = load_to_db(valid_records, db_path)
                result["loaded_to_db"] = count
                log.log_stage("LOAD", f"Written {count} records to DB.")

            if target in ("csv", "all"):
                path = load_to_csv(valid_records, output_dir)
                result["exported_csv"] = path
                log.log_stage("LOAD", f"CSV export: {path}")

            if target in ("json", "all"):
                path = load_to_json(valid_records, output_dir)
                result["exported_json"] = path
                log.log_stage("LOAD", f"JSON export: {path}")

            if target not in ("db", "csv", "json", "all"):
                raise ValueError(f"Unknown target: '{target}'. Choose from: db, csv, json, all")

        except Exception as e:
            log.log_stage("LOAD", f"FAILED — {e}")
            result["error"] = str(e)

    result["summary"] = log.summary()
    log.log_stage("PIPELINE", "Completed successfully.")
    return result


# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Helpdesk ETL Pipeline — Extract, Transform, Load ticket data."
    )
    parser.add_argument("--source", choices=["db", "csv", "json"], default="db",
                        help="Data source (default: db)")
    parser.add_argument("--target", choices=["db", "csv", "json", "all"], default="csv",
                        help="Data target (default: csv)")
    parser.add_argument("--input", dest="input_path", default=None,
                        help="Path to input file (required for csv/json source)")
    parser.add_argument("--db", dest="db_path", default="./backend/helpdesk.db",
                        help="SQLite DB path (default: ./backend/helpdesk.db)")
    parser.add_argument("--output-dir", default="./database",
                        help="Output directory for exports (default: ./database)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Run extract and transform only; skip load")

    args = parser.parse_args()

    result = run_pipeline(
        source=args.source,
        target=args.target,
        input_path=args.input_path,
        db_path=args.db_path,
        output_dir=args.output_dir,
        dry_run=args.dry_run,
    )

    print("\n─── Pipeline Result ───────────────────────────")
    print(json.dumps({k: v for k, v in result.items() if k != "summary"}, indent=2))
    print("───────────────────────────────────────────────\n")


if __name__ == "__main__":
    main()
