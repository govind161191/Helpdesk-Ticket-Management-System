"""
etl/transform.py — Transform phase of the ETL pipeline.

Responsibilities:
  1. Validate required fields
  2. Normalize text fields (strip whitespace, title-case names)
  3. Standardize controlled vocabulary (priority, status, category)
  4. Enrich records with derived fields (sla_flag, age_days)
  5. Deduplicate records
  6. Reject invalid records and log them
"""
import re
from datetime import datetime, timezone
from typing import List, Dict, Any, Tuple


# ─── Controlled Vocabularies ─────────────────────────────────────────────────

VALID_PRIORITIES = {"low", "medium", "high", "critical"}
VALID_STATUSES = {"open", "in progress", "resolved", "closed"}
VALID_CATEGORIES = {
    "vpn issue",
    "password reset",
    "software installation",
    "laptop issue",
    "email access",
    "network connectivity",
    "hardware request",
    "other",
}

# SLA thresholds in hours by priority
SLA_HOURS = {
    "Critical": 4,
    "High": 24,
    "Medium": 72,
    "Low": 168,
}

REQUIRED_FIELDS = ["employee_name", "department", "issue_category", "description", "priority"]


# ─── Individual Field Transformers ────────────────────────────────────────────

def _normalize_priority(raw: str) -> str:
    """Map raw priority string to a canonical value, default to 'Medium'."""
    normalized = raw.strip().lower()
    mapping = {
        "low": "Low",
        "l": "Low",
        "medium": "Medium",
        "med": "Medium",
        "m": "Medium",
        "high": "High",
        "h": "High",
        "critical": "Critical",
        "crit": "Critical",
        "c": "Critical",
    }
    return mapping.get(normalized, "Medium")


def _normalize_status(raw: str) -> str:
    """Map raw status string to a canonical value, default to 'Open'."""
    normalized = raw.strip().lower()
    mapping = {
        "open": "Open",
        "new": "Open",
        "in progress": "In Progress",
        "in-progress": "In Progress",
        "inprogress": "In Progress",
        "wip": "In Progress",
        "resolved": "Resolved",
        "done": "Resolved",
        "fixed": "Resolved",
        "closed": "Closed",
        "cancelled": "Closed",
    }
    return mapping.get(normalized, "Open")


def _normalize_category(raw: str) -> str:
    """Match raw category to closest valid category, default to 'Other'."""
    normalized = raw.strip().lower()
    for valid in VALID_CATEGORIES:
        if valid in normalized or normalized in valid:
            return valid.title()
    return "Other"


def _compute_age_days(created_at_str: Any) -> float:
    """Return how many days old the ticket is. Returns 0.0 if date is missing."""
    if not created_at_str:
        return 0.0
    try:
        created = datetime.fromisoformat(str(created_at_str).replace("Z", "+00:00"))
        now = datetime.now(timezone.utc)
        return round((now - created).total_seconds() / 86400, 2)
    except Exception:
        return 0.0


def _flag_sla_breach(priority: str, age_days: float) -> bool:
    """Return True if the ticket has exceeded its SLA threshold."""
    threshold_hours = SLA_HOURS.get(priority, 72)
    return (age_days * 24) > threshold_hours


# ─── Main Transform Function ──────────────────────────────────────────────────

def transform(raw_records: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Transform and validate a list of raw ticket records.

    Returns:
        Tuple of (valid_records, rejected_records).
        Each rejected record includes a 'rejection_reason' key.
    """
    valid: List[Dict[str, Any]] = []
    rejected: List[Dict[str, Any]] = []
    seen_keys: set = set()

    for idx, record in enumerate(raw_records):
        errors = []

        # 1. Validate required fields
        for field in REQUIRED_FIELDS:
            value = record.get(field, "")
            if not value or not str(value).strip():
                errors.append(f"Missing required field: '{field}'")

        if errors:
            record["rejection_reason"] = "; ".join(errors)
            rejected.append(record)
            continue

        # 2. Normalize text fields
        transformed = {}
        transformed["employee_name"] = str(record["employee_name"]).strip().title()
        transformed["department"] = str(record.get("department", "")).strip().title()
        transformed["description"] = str(record["description"]).strip()
        transformed["resolution_notes"] = str(record.get("resolution_notes", "") or "").strip() or None

        # 3. Standardize controlled vocabulary
        transformed["priority"] = _normalize_priority(str(record.get("priority", "Medium")))
        transformed["status"] = _normalize_status(str(record.get("status", "Open")))
        transformed["issue_category"] = _normalize_category(str(record.get("issue_category", "Other")))

        # 4. Carry over existing ticket_id if present (for updates)
        if "ticket_id" in record:
            transformed["ticket_id"] = record["ticket_id"]

        # 5. Preserve created_at if available
        transformed["created_at"] = record.get("created_at")

        # 6. Derive enriched fields
        age_days = _compute_age_days(transformed["created_at"])
        transformed["age_days"] = age_days
        transformed["sla_breached"] = _flag_sla_breach(transformed["priority"], age_days)

        # 7. Deduplicate by (employee_name, description) key
        dedup_key = (
            transformed["employee_name"].lower(),
            re.sub(r"\s+", " ", transformed["description"].lower())[:100],
        )
        if dedup_key in seen_keys:
            record["rejection_reason"] = "Duplicate record"
            rejected.append(record)
            continue
        seen_keys.add(dedup_key)

        valid.append(transformed)

    print(
        f"[TRANSFORM] {len(valid)} valid records, "
        f"{len(rejected)} rejected out of {len(raw_records)} total."
    )
    return valid, rejected
