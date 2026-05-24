"""
schemas.py — Pydantic schemas for request validation and response serialization.
"""
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field


# ─── Enums (as string literals for simplicity) ───────────────────────────────

VALID_PRIORITIES = ["Low", "Medium", "High", "Critical"]
VALID_STATUSES = ["Open", "In Progress", "Resolved", "Closed"]
VALID_CATEGORIES = [
    "VPN Issue",
    "Password Reset",
    "Software Installation",
    "Laptop Issue",
    "Email Access",
    "Network Connectivity",
    "Hardware Request",
    "Other",
]


# ─── Request Schemas ──────────────────────────────────────────────────────────

class TicketCreate(BaseModel):
    employee_name: str = Field(..., min_length=2, max_length=100, example="John Doe")
    department: str = Field(..., min_length=2, max_length=100, example="IT")
    issue_category: str = Field(..., example="VPN Issue")
    description: str = Field(..., min_length=10, example="Cannot connect to VPN from home network.")
    priority: str = Field(default="Medium", example="High")

    class Config:
        json_schema_extra = {
            "example": {
                "employee_name": "Jane Smith",
                "department": "Finance",
                "issue_category": "Password Reset",
                "description": "Unable to log into the corporate portal after password expiry.",
                "priority": "High",
            }
        }


class TicketUpdate(BaseModel):
    employee_name: Optional[str] = Field(None, max_length=100)
    department: Optional[str] = Field(None, max_length=100)
    issue_category: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    resolution_notes: Optional[str] = None


# ─── Response Schemas ─────────────────────────────────────────────────────────

class TicketResponse(BaseModel):
    ticket_id: int
    employee_name: str
    department: str
    issue_category: str
    description: str
    priority: str
    status: str
    resolution_notes: Optional[str]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    total: int
    tickets: list[TicketResponse]


class MessageResponse(BaseModel):
    message: str
    ticket_id: Optional[int] = None
