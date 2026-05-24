"""
main.py — FastAPI application entry point for the Helpdesk Ticket Management System.

Run with:
    uvicorn backend.main:app --reload
"""
from fastapi import FastAPI, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional

from .database import engine, get_db
from . import models, crud, schemas
from .routers import tickets as ticket_router
from .services import etl_service

# ─── Create tables ────────────────────────────────────────────────────────────
models.Base.metadata.create_all(bind=engine)

# ─── App instance ─────────────────────────────────────────────────────────────
app = FastAPI(
    title="Helpdesk Ticket Management System",
    description=(
        "A centralized web-based helpdesk system for managing employee IT support tickets. "
        "Phase 1 covers full CRUD operations, search/filter, and an ETL pipeline."
    ),
    version="1.0.0",
    contact={"name": "Support Team", "email": "support@company.com"},
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────────────────────────
app.include_router(ticket_router.router)
app.include_router(etl_service.router)


# ─── Health check ─────────────────────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Helpdesk Ticket Management System is running."}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


# ─── Dashboard ────────────────────────────────────────────────────────────────
@app.get("/dashboard", tags=["Dashboard"])
def dashboard(db: Session = Depends(get_db)):
    """Returns aggregate statistics for the dashboard."""
    stats = crud.get_dashboard_stats(db)
    # Serialize recent tickets manually (ORM objects → dicts)
    stats["recent_tickets"] = [
        schemas.TicketResponse.model_validate(t).model_dump()
        for t in stats["recent_tickets"]
    ]
    return stats


# ─── Search ───────────────────────────────────────────────────────────────────
@app.get("/search", response_model=schemas.TicketListResponse, tags=["Search"])
def search_tickets(
    keyword: Optional[str] = Query(None, description="Keyword to search in tickets"),
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by category"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db),
):
    """
    Search tickets by keyword (description, name, category, department).
    Optionally combine with status/category/priority filters.
    """
    if keyword:
        tickets = crud.search_tickets(db, keyword)
    else:
        tickets = crud.get_tickets(db, status=status, category=category, priority=priority)

    # Apply remaining filters on top of keyword results
    if keyword and (status or category or priority):
        if status:
            tickets = [t for t in tickets if t.status == status]
        if category:
            tickets = [t for t in tickets if t.issue_category == category]
        if priority:
            tickets = [t for t in tickets if t.priority == priority]

    return {"total": len(tickets), "tickets": tickets}
