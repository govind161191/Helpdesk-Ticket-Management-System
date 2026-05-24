"""
models.py — SQLAlchemy ORM models for the Helpdesk Ticket Management System.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from .database import Base


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    employee_name = Column(String(100), nullable=False, index=True)
    department = Column(String(100), nullable=False)
    issue_category = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    priority = Column(String(20), nullable=False, default="Medium")
    status = Column(String(20), nullable=False, default="Open", index=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
