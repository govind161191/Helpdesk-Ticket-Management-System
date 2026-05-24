"""
routers/tickets.py — FastAPI router for all ticket-related endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from .. import crud, schemas
from ..database import get_db

router = APIRouter(prefix="/tickets", tags=["Tickets"])


# ─── GET /tickets ─────────────────────────────────────────────────────────────

@router.get("/", response_model=schemas.TicketListResponse, summary="List all tickets")
def list_tickets(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=500, description="Max records to return"),
    status: Optional[str] = Query(None, description="Filter by status"),
    category: Optional[str] = Query(None, description="Filter by issue category"),
    priority: Optional[str] = Query(None, description="Filter by priority"),
    db: Session = Depends(get_db),
):
    tickets = crud.get_tickets(db, skip=skip, limit=limit, status=status,
                               category=category, priority=priority)
    total = crud.count_tickets(db, status=status, category=category, priority=priority)
    return {"total": total, "tickets": tickets}


# ─── GET /tickets/{id} ────────────────────────────────────────────────────────

@router.get("/{ticket_id}", response_model=schemas.TicketResponse, summary="Get ticket by ID")
def get_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = crud.get_ticket(db, ticket_id)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return ticket


# ─── POST /tickets ────────────────────────────────────────────────────────────

@router.post(
    "/",
    response_model=schemas.TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new ticket",
)
def create_ticket(ticket: schemas.TicketCreate, db: Session = Depends(get_db)):
    return crud.create_ticket(db, ticket)


# ─── PUT /tickets/{id} ────────────────────────────────────────────────────────

@router.put("/{ticket_id}", response_model=schemas.TicketResponse, summary="Update a ticket")
def update_ticket(
    ticket_id: int, ticket_data: schemas.TicketUpdate, db: Session = Depends(get_db)
):
    ticket = crud.update_ticket(db, ticket_id, ticket_data)
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return ticket


# ─── DELETE /tickets/{id} ─────────────────────────────────────────────────────

@router.delete(
    "/{ticket_id}",
    response_model=schemas.MessageResponse,
    summary="Delete a ticket",
)
def delete_ticket(ticket_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_ticket(db, ticket_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Ticket {ticket_id} not found")
    return {"message": f"Ticket {ticket_id} deleted successfully", "ticket_id": ticket_id}
