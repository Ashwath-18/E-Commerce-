"""Shared helpers for CRUD modules."""

import re


def exact_ci(value):
    """Case-insensitive exact-match Mongo condition."""
    return {"$regex": f"^{re.escape(str(value).strip())}$", "$options": "i"}


def normalize_id(value):
    """IDs are stored upper-case, like the imported dataset."""
    return str(value).strip().upper()