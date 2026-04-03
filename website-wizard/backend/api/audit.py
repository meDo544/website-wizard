from typing import Optional, Any, Dict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, HttpUrl
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.models.audit import Audit
from backend.queue.redis_queue import enqueue_audit

router = APIRouter(prefix="/audit", tags=["audit"])


# -----------------------------
# Request Models
# -----------------------------

class AuditStartRequest(BaseModel):
    url: HttpUrl


# -----------------------------
# Response Models
# -----------------------------

class AuditStatusResponse(BaseModel):
    id: int
    url: str
    status: str
    overall_score: Optional[int] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class AuditReportResponse(BaseModel):
    id: int
    url: str
    status: str
    overall_score: Optional[int]
    performance_score: Optional[int]
    seo_score: Optional[int]
    accessibility_score: Optional[int]
    best_practices_score: Optional[int]

    crawl_data: Optional[Dict[str, Any]]
    gpt_report: Optional[Dict[str, Any]]

    error_message: Optional[str]

    class Config:
        from_attributes = True


# -----------------------------
# Start Audit
# -----------------------------

@router.post("/start")
def start_audit(payload: AuditStartRequest, db: Session = Depends(get_db)):
    audit = Audit(
        url=str(payload.url),
        status="queued",
    )

    db.add(audit)
    db.commit()
    db.refresh(audit)

    # ✅ FIX: Send FULL job payload (not just ID)
    job = {
        "audit_id": audit.id,
        "url": audit.url
    }

    print("🚀 Enqueueing job:", job)  # DEBUG

    enqueue_audit(job)

    return {
        "audit_id": audit.id,
        "status": audit.status,
        "url": audit.url
    }


# -----------------------------
# Audit Status
# -----------------------------

@router.get("/{audit_id}", response_model=AuditStatusResponse)
def get_audit_status(audit_id: int, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()

    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    return audit


# -----------------------------
# Full Audit Report
# -----------------------------

@router.get("/{audit_id}/report", response_model=AuditReportResponse)
def get_audit_report(audit_id: int, db: Session = Depends(get_db)):
    audit = db.query(Audit).filter(Audit.id == audit_id).first()

    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    return audit