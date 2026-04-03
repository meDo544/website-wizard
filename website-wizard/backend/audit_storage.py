import json
import os
from datetime import datetime
from typing import Dict


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
AUDIT_DIR = os.path.join(BASE_DIR, "data", "audits")


def save_audit(audit: Dict, phase: str, identifier: str) -> str:
    """
    Save audit JSON to data/audits/{before|after}/
    """
    if phase not in ("before", "after"):
        raise ValueError("phase must be 'before' or 'after'")

    target_dir = os.path.join(AUDIT_DIR, phase)
    os.makedirs(target_dir, exist_ok=True)

    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filename = f"{identifier}_{timestamp}.json"
    filepath = os.path.join(target_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(audit, f, indent=2)

    return filepath
