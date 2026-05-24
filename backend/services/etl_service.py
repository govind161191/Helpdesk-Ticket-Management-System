"""
backend/services/etl_service.py — FastAPI-integrated ETL service.

Exposes an API router so the ETL pipeline can be triggered via HTTP:
    POST /etl/run        — Run full pipeline
    GET  /etl/status     — Check last pipeline run result
"""
from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Optional
import sys
from pathlib import Path

# Ensure the project root is in path so we can import the etl package
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from etl.etl_pipeline import run_pipeline

router = APIRouter(prefix="/etl", tags=["ETL Pipeline"])

# In-memory store for last pipeline run result
_last_run_result: dict = {}


class ETLRequest(BaseModel):
    source: str = "db"          # "db" | "csv" | "json"
    target: str = "csv"         # "db" | "csv" | "json" | "all"
    input_path: Optional[str] = None
    db_path: str = "./backend/helpdesk.db"
    output_dir: str = "./database"
    dry_run: bool = False


class ETLResponse(BaseModel):
    status: str
    message: str
    result: Optional[dict] = None


def _run_etl_task(params: ETLRequest):
    """Background task: run the ETL pipeline and cache the result."""
    global _last_run_result
    result = run_pipeline(
        source=params.source,
        target=params.target,
        input_path=params.input_path,
        db_path=params.db_path,
        output_dir=params.output_dir,
        dry_run=params.dry_run,
    )
    _last_run_result = result


@router.post("/run", response_model=ETLResponse, summary="Trigger ETL pipeline")
def trigger_etl(params: ETLRequest, background_tasks: BackgroundTasks):
    """
    Trigger the ETL pipeline asynchronously.

    The pipeline runs in the background; poll GET /etl/status for results.

    **source**: db | csv | json
    **target**: db | csv | json | all
    """
    background_tasks.add_task(_run_etl_task, params)
    return {
        "status": "started",
        "message": (
            f"ETL pipeline started in background. "
            f"Source: '{params.source}' → Target: '{params.target}'. "
            f"Poll GET /etl/status for results."
        ),
        "result": None,
    }


@router.post("/run/sync", response_model=ETLResponse, summary="Trigger ETL pipeline (synchronous)")
def trigger_etl_sync(params: ETLRequest):
    """
    Trigger the ETL pipeline synchronously and return the result immediately.
    Use for small datasets or testing; for large data use the async /run endpoint.
    """
    global _last_run_result
    result = run_pipeline(
        source=params.source,
        target=params.target,
        input_path=params.input_path,
        db_path=params.db_path,
        output_dir=params.output_dir,
        dry_run=params.dry_run,
    )
    _last_run_result = result

    if "error" in result:
        raise HTTPException(status_code=500, detail=result["error"])

    return {
        "status": "completed",
        "message": (
            f"ETL completed. "
            f"Extracted: {result.get('extracted', 'N/A')}, "
            f"Valid: {result.get('valid', 'N/A')}, "
            f"Rejected: {result.get('rejected', 'N/A')}."
        ),
        "result": result,
    }


@router.get("/status", summary="Get last ETL pipeline run status")
def etl_status():
    """Return the cached result from the most recent ETL pipeline run."""
    if not _last_run_result:
        return {"status": "no_runs", "message": "No ETL pipeline has been run yet."}
    return {"status": "completed", "result": _last_run_result}
