"""
crud.py — Database CRUD operations for Ticket model.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from . import models, schemas


# ─── CREATE ──────────────────────────────────────────────────────────────────

def create_ticket(db: Session, ticket: schemas.TicketCreate) -> models.Ticket:
    """Insert a new ticket record into the database."""
    db_ticket = models.Ticket(
        employee_name=ticket.employee_name,
        department=ticket.department,
        issue_category=ticket.issue_category,
        description=ticket.description,
        priority=ticket.priority,
        status="Open",
    )
    db.add(db_ticket)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


# ─── READ ─────────────────────────────────────────────────────────────────────

def get_ticket(db: Session, ticket_id: int) -> Optional[models.Ticket]:
    """Fetch a single ticket by its primary key."""
    return db.query(models.Ticket).filter(models.Ticket.ticket_id == ticket_id).first()


def get_tickets(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
) -> List[models.Ticket]:
    """Fetch all tickets with optional status/category/priority filters."""
    query = db.query(models.Ticket)
    if status:
        query = query.filter(models.Ticket.status == status)
    if category:
        query = query.filter(models.Ticket.issue_category == category)
    if priority:
        query = query.filter(models.Ticket.priority == priority)
    return query.offset(skip).limit(limit).all()


def count_tickets(
    db: Session,
    status: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
) -> int:
    """Count tickets matching optional filters."""
    query = db.query(models.Ticket)
    if status:
        query = query.filter(models.Ticket.status == status)
    if category:
        query = query.filter(models.Ticket.issue_category == category)
    if priority:
        query = query.filter(models.Ticket.priority == priority)
    return query.count()


def search_tickets(db: Session, keyword: str) -> List[models.Ticket]:
    """Full-text keyword search across description, employee name, and category."""
    pattern = f"%{keyword}%"
    return (
        db.query(models.Ticket)
        .filter(
            or_(
                models.Ticket.description.ilike(pattern),
                models.Ticket.employee_name.ilike(pattern),
                models.Ticket.issue_category.ilike(pattern),
                models.Ticket.department.ilike(pattern),
            )
        )
        .all()
    )


# ─── UPDATE ───────────────────────────────────────────────────────────────────

def update_ticket(
    db: Session, ticket_id: int, ticket_data: schemas.TicketUpdate
) -> Optional[models.Ticket]:
    """Partially update a ticket. Only provided fields are changed."""
    db_ticket = get_ticket(db, ticket_id)
    if not db_ticket:
        return None
    update_data = ticket_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_ticket, field, value)
    db.commit()
    db.refresh(db_ticket)
    return db_ticket


# ─── DELETE ───────────────────────────────────────────────────────────────────

def delete_ticket(db: Session, ticket_id: int) -> bool:
    """Delete a ticket. Returns True if deleted, False if not found."""
    db_ticket = get_ticket(db, ticket_id)
    if not db_ticket:
        return False
    db.delete(db_ticket)
    db.commit()
    return True


# ─── DASHBOARD STATS ─────────────────────────────────────────────────────────

def get_dashboard_stats(db: Session) -> dict:
    """Aggregate counts for the dashboard summary."""
    total = db.query(models.Ticket).count()
    open_count = db.query(models.Ticket).filter(models.Ticket.status == "Open").count()
    in_progress = db.query(models.Ticket).filter(models.Ticket.status == "In Progress").count()
    resolved = db.query(models.Ticket).filter(models.Ticket.status == "Resolved").count()
    closed = db.query(models.Ticket).filter(models.Ticket.status == "Closed").count()
    critical = db.query(models.Ticket).filter(models.Ticket.priority == "Critical").count()
    recent = (
        db.query(models.Ticket)
        .order_by(models.Ticket.created_at.desc())
        .limit(5)
        .all()
    )
    return {
        "total": total,
        "open": open_count,
        "in_progress": in_progress,
        "resolved": resolved,
        "closed": closed,
        "critical": critical,
        "recent_tickets": recent,
    }
